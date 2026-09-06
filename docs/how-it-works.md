# How it works

The mod ships no audio. It adds the Wwise objects a radio track needs, points them at a file the
game already installs, and registers the track with the station at runtime.

## A radio playlist is not TweakDB

`RadioStation.GrowlFM` holds three fields: `displayName`, `icon`, `index`. It holds no tracks.
TweakXL and ArchiveXL cannot reach a station's playlist.

The track list lives in two cooked resources:

| Resource | Holds |
| --- | --- |
| `base\sound\event\eventsmetadata.json` | event name to Wwise id, and the duration the station schedules against |
| `base\sound\metadata\cooked_metadata.audio_metadata` | the `audioRadioTrack` rows, and each station's `tracks` array |

Both are patched in memory as they load. No file on disk is modified or replaced.

Phantom Liberty keeps a second cooked metadata resource at `ep1\sound\metadata\`. It contains no
radio station records, so patching the base resource covers every station.

## What a vanilla radio track is

```text
Event --Play(0x0403)--> MusicSegment --> MusicTrack --> <id>.wem   (streamed)
                             |
                             +-- parent: the station's MusicPlaylist
```

For Growl FM the playlist is `375417660`, which parents the thirteen stock segments and nothing
else. A segment parented there inherits the station's mixing.

Station music is split across `radio.bnk` and `cp_music.bnk`. A given station's tracks may be in
either.

## The soundbank

`tools/make_bank.py` builds four objects: a MusicTrack over the source file, a MusicSegment holding
it, an Event, and a Play action. The segment and track are cloned from `mus_radio_12_afterlife`, so
every field the generator does not overwrite keeps a Growl FM track's routing, attenuation and
automation.

A Play action ends with the bank id of the bank holding its target. A bank id is the FNV-1 32-bit
hash of the bank name, so a mod bank can name a vanilla one.

The generator asserts every field it reads, so a game patch that moves a field fails the build.

## Constraints

A bank that violates any of these still loads with `AK_Success`, and then plays nothing or plays
wrongly.

**Fade-out automation.** A MusicTrack stores its fade as automation points in a variable-length
block after the playlist items. Those times are 32-bit floats in seconds; every other duration in
the record is a 64-bit double in milliseconds. Cloned points therefore keep the template's timing
and must be moved to the end of the new clip, or the track falls silent at the template's length
and plays inaudibly until the declared duration elapses.

**Field offsets.** A MusicTrack's fields sit after its source block, which is fourteen bytes per
source. Offsets valid for a single-source track read a two-source track's second plugin id as a
playlist-item count. Read the source count and walk the record.

**Declared duration.** `minDuration` must be the audible length, not the file length. Ten of the
thirteen Growl FM tracks trim one to eight seconds off the tail and declare the trimmed value. An
untrimmed declaration leaves the station waiting out trailing silence before the next track.

**AudioXL manifest.** A manifest with `banks` and no `sounds` key returns before the banks loop,
loading nothing and logging nothing. Include `"sounds": []`.

## Testing an event by name

`GameInstance.GetAudioSystem().Play(name)` resolves a CName to a Wwise id through
`eventsmetadata.json`. An event that exists in a loaded bank but has no row in that table cannot be
posted by name and fails silently. Any event to be tested from the console must be registered the
same way the shipped track is.

## Untested

Neither of these is known either way, and neither affects the shipped mod, which uses one track in
one bank with a segment it owns.

- Whether a segment defined in another bank can be targeted successfully, and whether it sounds
  while its own hierarchy is inactive.
- Whether one bank can carry several tracks, and whether several banks can be loaded together.
  Vanilla banks hold hundreds of events each, so there is no reason to expect a low limit.

## Patching the resources

`Resource/Load` fires only while a resource is loading, so it does not fire for a resource another
mod has already loaded. AudioXL loads the cooked metadata itself. The mod therefore registers the
callback and also requests the resource from the depot with a token, and the patch is idempotent.

Without the second path the event registers but the station is never modified, so the track plays
from the console and never on the radio.

## The track title

The station displays `Artist - Title` from an onscreens entry shipped in this mod's archive. Its
`primaryKey` is `0`, so ArchiveXL derives the keys: it registers the entry under `FNV1a32` of the
secondary key, and again under `FNV1a64` with the string cleared. `audioRadioTrack.primaryLocKey` is
a `Uint64`, so it takes the 64-bit hash.

Vanilla does not localize most track titles. Japanese localizes the station name but leaves titles
in Latin script, identical to English. Russian transliterates the artist and separates it with a
non-breaking space and an em dash. This mod maps one Latin string to every language. The first
language listed in the `.xl` is the fallback for any language omitted.

## Verifying a change

The bank and the station registration are independent and need separate checks.

- **The bank** - `Game.GetAudioSystem():Play("mus_radio_12_hardest_to_be")` in the CET console. This
  bypasses the station, so it tests the bank only.
- **The station** - the log reports the track count rising to fourteen, and the song then appears in
  rotation while driving. The game has no track skip, so this takes time.
