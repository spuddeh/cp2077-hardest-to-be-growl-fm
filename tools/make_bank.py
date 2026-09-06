r"""Build the soundbank that puts Hardest to Be on Growl FM.

The song is already in the game as base\sound\soundbanks\media\528262674.wem, but the only
node that touches it is a seven-second outro sting for the Alex heart-to-heart scene. This bank
adds the four Wwise objects a radio track needs - a MusicTrack over the whole file, a MusicSegment
holding it, and an Event with a Play action - and parents the segment to Growl FM's own playlist so
the mix matches the other thirteen tracks.

The segment and track are cloned from mus_radio_12_afterlife rather than written from scratch, so
every field this script does not touch already carries a Growl FM track's settings.

Run:  python make_bank.py <radio.bnk> <cp_music.bnk> <out.bnk>
"""
import struct
import sys

BANK_NAME  = "hardest_to_be_growl"
EVENT_NAME = "mus_radio_12_hardest_to_be"

TEMPLATE_EVENT   = 18591205    # mus_radio_12_afterlife
GROWL_PLAYLIST   = 375417660   # parents all thirteen Growl FM segments
SOURCE_WEM       = 528262674
SOURCE_TRACK     = 491378111   # the outro sting, read for its media size and true duration

BANK_VERSION = 150
LANGUAGE_ID  = 393239870


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
        tag = data[offset:offset + 4]
        length = struct.unpack_from("<I", data, offset + 4)[0]
        if tag == b"HIRC":
            break
        offset += 8 + length
    pos = offset + 8
    count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    objects = {}
    for _ in range(count):
        obj_type = data[pos]
        size = struct.unpack_from("<I", data, pos + 1)[0]
        obj_id = struct.unpack_from("<I", data, pos + 5)[0]
        objects[obj_id] = (obj_type, data[pos + 5:pos + 5 + size])
        pos += 5 + size
    return objects


def put_u32(buf, offset, value):
    struct.pack_into("<I", buf, offset, value)


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


def build(radio_path, music_path):
    radio = read_hirc(radio_path)
    music = read_hirc(music_path)

    event_type, event_body = radio[TEMPLATE_EVENT]
    assert event_type == 4 and event_body[4] == 1, "template event is not a single-action event"
    tmpl_action_id = struct.unpack_from("<I", event_body, 5)[0]
    action_type, action_body = radio[tmpl_action_id]
    assert action_type == 3 and struct.unpack_from("<H", action_body, 4)[0] == 0x0403

    tmpl_segment_id = struct.unpack_from("<I", action_body, 6)[0]
    segment_type, segment_body = radio[tmpl_segment_id]
    assert segment_type == 10, "template Play action does not target a MusicSegment"

    tmpl_track_id = struct.unpack_from("<I", segment_body, 40)[0]
    track_type, track_body = radio[tmpl_track_id]
    assert track_type == 11, "template segment does not hold a MusicTrack"
    assert struct.unpack_from("<I", segment_body, 13)[0] == GROWL_PLAYLIST

    # The sting carries the file's real length; play it whole, so no trim and no offset.
    _, sting = music[SOURCE_TRACK]
    assert struct.unpack_from("<I", sting, 14)[0] == SOURCE_WEM
    source_size = struct.unpack_from("<I", sting, 18)[0]
    source_duration = struct.unpack_from("<d", sting, 63)[0]

    bank_id    = fnv(BANK_NAME)
    event_id   = fnv(EVENT_NAME)
    action_id  = fnv(EVENT_NAME + "_play")
    segment_id = fnv(EVENT_NAME + "_segment")
    track_id   = fnv(EVENT_NAME + "_track")

    tmpl_source     = struct.unpack_from("<I", track_body, 14)[0]
    tmpl_size       = struct.unpack_from("<I", track_body, 18)[0]
    tmpl_end_trim   = struct.unpack_from("<d", track_body, 55)[0]
    tmpl_duration   = struct.unpack_from("<d", track_body, 63)[0]
    tmpl_seg_length = struct.unpack_from("<d", segment_body, 71)[0]
    playable        = tmpl_duration + tmpl_end_trim
    assert abs(tmpl_seg_length - playable) < 0.001, "template segment and track disagree on length"

    track = bytearray(track_body)
    assert replace_u32(track, tmpl_track_id, track_id) == 1
    assert replace_u32(track, tmpl_source, SOURCE_WEM) == 2
    assert replace_u32(track, tmpl_size, source_size) == 1
    assert replace_u32(track, tmpl_segment_id, segment_id) == 1
    assert replace_f64(track, tmpl_end_trim, 0.0) >= 1
    assert replace_f64(track, tmpl_duration, source_duration) >= 1

    segment = bytearray(segment_body)
    assert replace_u32(segment, tmpl_segment_id, segment_id) == 1
    assert replace_u32(segment, tmpl_track_id, track_id) == 1
    assert replace_f64(segment, tmpl_seg_length, source_duration) == 2

    action = bytearray(action_body)
    put_u32(action, 0, action_id)
    put_u32(action, 6, segment_id)
    put_u32(action, 14, bank_id)

    event = bytearray(event_body)
    put_u32(event, 0, event_id)
    put_u32(event, 5, action_id)

    hirc = struct.pack("<I", 4)
    for obj_type, body in ((11, track), (10, segment), (3, action), (4, event)):
        hirc += bytes([obj_type]) + struct.pack("<I", len(body)) + bytes(body)

    bkhd = struct.pack("<IIIIII", BANK_VERSION, bank_id, LANGUAGE_ID, 16, 476, 0)
    bkhd += struct.pack("<IIII", bank_id, event_id, segment_id, track_id)

    data = b"BKHD" + struct.pack("<I", len(bkhd)) + bkhd
    data += b"HIRC" + struct.pack("<I", len(hirc)) + hirc
    return data, dict(bank=bank_id, event=event_id, action=action_id,
                      segment=segment_id, track=track_id,
                      duration_ms=source_duration, media_size=source_size)


if __name__ == "__main__":
    radio, music, out = sys.argv[1], sys.argv[2], sys.argv[3]
    data, ids = build(radio, music)
    open(out, "wb").write(data)
    print(f"{out}  {len(data)} bytes")
    for k, v in ids.items():
        print(f"  {k:11} {v}")
    print(f"  duration for eventsmetadata: {ids['duration_ms'] / 1000.0:.4f} s")
