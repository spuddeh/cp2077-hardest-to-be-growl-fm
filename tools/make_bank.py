r"""Build a soundbank that plays a source file the game already ships as a Growl FM radio track.

A vanilla radio track is an Event whose Play action targets a MusicSegment holding a MusicTrack,
with the segment parented to the station's own playlist. This clones that whole shape from
mus_radio_12_afterlife and retargets it, so every field not named below already carries a Growl FM
track's settings.

The clone is what makes it work. An Event that points straight at a segment inside another bank's
hierarchy loads without error and plays nothing when that hierarchy is not live - a quest's music
switch container, for instance. Owning the segment avoids that.

Run:  python make_bank.py <radio.bnk> <cp_music.bnk> <out.bnk> [event_name source_wem duration_ms]
With no trailing arguments it builds the shipped bank.
"""
import struct
import sys

SHIPPED = ("mus_radio_12_hardest_to_be", 528262674, 206897.3958333333)

TEMPLATE_EVENT = 18591205    # mus_radio_12_afterlife
GROWL_PLAYLIST = 375417660   # parents all thirteen Growl FM segments

BANK_VERSION = 150
LANGUAGE_ID = 393239870


def fnv(name):
    h = 2166136261
    for b in name.lower().encode():
        h = (h * 16777619) & 0xFFFFFFFF
        h ^= b
    return h


def read_hirc(path):
    data = open(path, "rb").read()
    offset = 0
    while offset < len(data) - 8:
        if data[offset:offset + 4] == b"HIRC":
            break
        offset += 8 + struct.unpack_from("<I", data, offset + 4)[0]
    pos = offset + 8
    count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    objects = {}
    for _ in range(count):
        size = struct.unpack_from("<I", data, pos + 1)[0]
        obj_id = struct.unpack_from("<I", data, pos + 5)[0]
        objects[obj_id] = (data[pos], data[pos + 5:pos + 5 + size])
        pos += 5 + size
    return objects


def replace_u32(buf, old, new):
    hits = 0
    for i in range(len(buf) - 3):
        if struct.unpack_from("<I", buf, i)[0] == old:
            struct.pack_into("<I", buf, i, new)
            hits += 1
    return hits


def replace_f64(buf, old, new):
    hits = 0
    for i in range(len(buf) - 7):
        if struct.unpack_from("<d", buf, i)[0] == old:
            struct.pack_into("<d", buf, i, new)
            hits += 1
    return hits


def build(radio_path, music_path, event_name, source_wem, source_duration, bank_name):
    radio = read_hirc(radio_path)

    event_type, event_body = radio[TEMPLATE_EVENT]
    assert event_type == 4 and event_body[4] == 1, "template event is not a single-action event"
    tmpl_action_id = struct.unpack_from("<I", event_body, 5)[0]
    action_type, action_body = radio[tmpl_action_id]
    assert action_type == 3 and struct.unpack_from("<H", action_body, 4)[0] == 0x0403

    tmpl_segment_id = struct.unpack_from("<I", action_body, 6)[0]
    segment_type, segment_body = radio[tmpl_segment_id]
    assert segment_type == 10, "template Play action does not target a MusicSegment"
    assert struct.unpack_from("<I", segment_body, 13)[0] == GROWL_PLAYLIST

    tmpl_track_id = struct.unpack_from("<I", segment_body, 40)[0]
    track_type, track_body = radio[tmpl_track_id]
    assert track_type == 11, "template segment does not hold a MusicTrack"

    # The prefetch size lives in whichever track already reads this file.
    media_size = None
    for objects in (radio, read_hirc(music_path)):
        for obj_type, body in objects.values():
            if obj_type == 11 and len(body) > 22 and struct.unpack_from("<I", body, 14)[0] == source_wem:
                media_size = struct.unpack_from("<I", body, 18)[0]
                break
        if media_size is not None:
            break
    assert media_size is not None, f"no MusicTrack reads {source_wem}, so its prefetch size is unknown"

    bank_id = fnv(bank_name)
    event_id = fnv(event_name)
    action_id = fnv(event_name + "_play")
    segment_id = fnv(event_name + "_segment")
    track_id = fnv(event_name + "_track")

    tmpl_source = struct.unpack_from("<I", track_body, 14)[0]
    tmpl_size = struct.unpack_from("<I", track_body, 18)[0]
    tmpl_end_trim = struct.unpack_from("<d", track_body, 55)[0]
    tmpl_duration = struct.unpack_from("<d", track_body, 63)[0]
    tmpl_seg_length = struct.unpack_from("<d", segment_body, 71)[0]
    assert abs(tmpl_seg_length - (tmpl_duration + tmpl_end_trim)) < 0.001, \
        "template segment and track disagree on length"

    track = bytearray(track_body)
    assert replace_u32(track, tmpl_track_id, track_id) == 1
    assert replace_u32(track, tmpl_source, source_wem) == 2
    assert replace_u32(track, tmpl_size, media_size) == 1
    assert replace_u32(track, tmpl_segment_id, segment_id) == 1
    assert replace_f64(track, tmpl_end_trim, 0.0) >= 1
    assert replace_f64(track, tmpl_duration, source_duration) >= 1

    segment = bytearray(segment_body)
    assert replace_u32(segment, tmpl_segment_id, segment_id) == 1
    assert replace_u32(segment, tmpl_track_id, track_id) == 1
    assert replace_f64(segment, tmpl_seg_length, source_duration) == 2

    action = bytearray(action_body)
    struct.pack_into("<I", action, 0, action_id)
    struct.pack_into("<I", action, 6, segment_id)
    struct.pack_into("<I", action, 14, bank_id)

    event = bytearray(event_body)
    struct.pack_into("<I", event, 0, event_id)
    struct.pack_into("<I", event, 5, action_id)

    hirc = struct.pack("<I", 4)
    for obj_type, body in ((11, track), (10, segment), (3, action), (4, event)):
        hirc += bytes([obj_type]) + struct.pack("<I", len(body)) + bytes(body)

    bkhd = struct.pack("<IIIIII", BANK_VERSION, bank_id, LANGUAGE_ID, 16, 476, 0)
    bkhd += struct.pack("<IIII", bank_id, event_id, segment_id, track_id)

    data = b"BKHD" + struct.pack("<I", len(bkhd)) + bkhd
    data += b"HIRC" + struct.pack("<I", len(hirc)) + hirc
    return data, dict(bank=bank_id, event=event_id, action=action_id,
                      segment=segment_id, track=track_id, media_size=media_size)


if __name__ == "__main__":
    radio, music, out = sys.argv[1], sys.argv[2], sys.argv[3]
    if len(sys.argv) > 4:
        event_name, source_wem, source_duration = sys.argv[4], int(sys.argv[5]), float(sys.argv[6])
    else:
        event_name, source_wem, source_duration = SHIPPED
    bank_name = out.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]

    data, ids = build(radio, music, event_name, source_wem, source_duration, bank_name)
    open(out, "wb").write(data)
    print(f"{out}  {len(data)} bytes")
    print(f"  bank  {bank_name} ({ids['bank']})")
    print(f"  event {event_name} ({ids['event']})")
    print(f"  source {source_wem}, {source_duration / 1000.0:.4f} s")
