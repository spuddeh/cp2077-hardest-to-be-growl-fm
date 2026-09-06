# How it works

The mod ships no audio. It adds the Wwise objects a radio track needs, points them at a file the
game already installs, and tells the station about it at runtime.

## A radio playlist is not TweakDB

`RadioStation.GrowlFM` holds three fields: `displayName`, `icon`, `index`. There are no tracks in
it. TweakXL and ArchiveXL cannot reach a station's playlist, and looking for a TweakDB record that
holds one is wasted effort.

The track list lives in two cooked resources:

| Resource | Holds |
| --- | --- |
| `base\sound\event\eventsmetadata.json` | event name to Wwise id, and the duration the station schedules against |
| `base\sound\metadata\cooked_metadata.audio_metadata` | the `audioRadioTrack` rows, and each station's `tracks` array |

Both are patched in memory as they load. Nothing on disk is modified, and no vanilla file is
replaced, so the mod cannot conflict with anything that edits those files a different way.

Phantom Liberty keeps a second cooked metadata resource at `ep1\sound\metadata\`, but it contains
no radio station records at all, so patching the base one is complete.

## What a vanilla radio track is

```text
Event --Play(0x0403)--> MusicSegment --> MusicTrack --> <id>.wem   (streamed)
                             |
                             +-- parent: the station's MusicPlaylist
```

For Growl FM that playlist is `375417660`. It parents exactly the thirteen stock segments and
nothing else, so a segment parented there inherits the station's mixing and sits at the same level
as everything else on the dial.

Station music lives in both `radio.bnk` and `cp_music.bnk`, and a given station's tracks may be in
either.

## The soundbank

`tools/make_bank.py` builds four objects: a MusicTrack over the source file, a MusicSegment holding
it, an Event, and a Play action. The segment and track are **cloned from `mus_radio_12_afterlife`**
rather than written from scratch, so every field the generator does not touch already carries a
Growl FM track's own settings - routing, attenuation, automation.

The Play action ends with the bank id of the bank its target lives in, and a bank id is the FNV-1
32-bit hash of the bank's name, so a mod bank can name a vanilla one.

The generator asserts every field it reads. A game patch that moves a field fails the build rather
than producing a bank that loads and misbehaves.

## Things that look right and are not

Each of these produces a bank that loads with `AK_Success` and then plays nothing, or plays
wrongly. A clean load proves very little.

**Own the segment.** An Event aimed at a segment inside another bank's hierarchy loads without
error and stays silent whenever that hierarchy is not live - a quest's music switch container, for
example. Owning the segment and parenting it to the station's playlist is what makes it play.

**The fade-out is automation, in seconds.** A MusicTrack carries its fade as automation points
whose times are 32-bit floats in seconds, in a variable-length block after the playlist items,
while every other duration in the record is a 64-bit double in milliseconds. A clone that keeps
them fades to silence at the *template's* length and then plays on inaudibly to the declared
duration. The track sounds perfect right up until it stops.

**Field positions depend on the source count.** A MusicTrack carrying two sources pushes everything
after the source block along by fourteen bytes. Read the count and walk the record; a fixed offset
reads the second source's plugin id as a playlist-item count.

**One bank.** Three of these banks loaded together silenced each other, including a control on a
source known to play, and a bank holding six events played only its first. Only one track per bank
is proven.

**The duration must be the audible length.** Ten of the thirteen Growl FM tracks trim one to eight
seconds off the tail, and `minDuration` matches the trimmed length. Declare the raw file length and
the station waits out the silence before moving on.

**AudioXL needs a `sounds` key to load banks.** A manifest carrying `banks` and no `sounds` returns
from the loader before the banks loop, loading nothing and logging nothing. `"sounds": []` gets past
it.

## Patching the resources

`Resource/Load` fires only *while* a resource is loading, so it never arrives for a resource another
mod already pulled in - AudioXL loads the cooked metadata itself. The mod registers the callback
**and** asks the depot for the resource with a token, and the patch is safe to run twice.

Get this wrong and the event registers, the station is never touched, and the track plays from the
console but never on the radio.

## The track title

The station shows `Artist - Title` from an onscreens entry, shipped in this mod's archive. Its
`primaryKey` is `0`, which makes ArchiveXL derive the keys: it registers the entry under `FNV1a32`
of the secondary key, and again under `FNV1a64` with the string dropped. `audioRadioTrack`'s
`primaryLocKey` is a `Uint64`, so it is the 64-bit hash.

Vanilla mostly does not localize track titles. Japanese localizes the station name but leaves titles
in Latin script, identical to English; Russian transliterates the artist and uses a non-breaking
space with an em dash. One Latin string is mapped to every language here, and the first language
listed in the `.xl` is the fallback for any omitted.

## Verifying a change

Two halves, and both need checking:

- **The bank** - `Game.GetAudioSystem():Play("mus_radio_12_hardest_to_be")` in the CET console.
  This bypasses the station, so it proves the bank and nothing else.
- **The station** - the log should report the track count rising to fourteen, then the song has to
  come up in rotation while driving. Skipping tracks is not a vanilla feature, so this takes
  patience.
