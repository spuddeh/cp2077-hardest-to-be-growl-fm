# Changelog

## [1.0.0] - 2026-09-07

First release.

### Added
- `hardest_to_be_growl.bnk`, built by `tools/make_bank.py`: a MusicTrack over
  `base\sound\soundbanks\mediaǲ143559.wem`, a MusicSegment holding it, an Event and a Play
  action. The segment and track are cloned from `mus_radio_12_afterlife`, so every field the
  generator does not overwrite keeps a Growl FM track's own settings, and the segment is parented
  to Growl FM's playlist `375417660`. The mod ships no audio.
- `HardestToBeGrowlFM.reds`: appends the event to `eventsmetadata.json` with the source's audible
  length, and appends an `audioRadioTrack` row plus the station entry to
  `cooked_metadata.audio_metadata`. Each resource is reached both by `Resource/Load` and by a depot
  token, because the callback never fires for a resource another mod has already loaded. Both
  patches are idempotent.
- `HardestToBeGrowlFM.archive` and its `.xl`: one onscreens entry giving the track title
  `P.T. Adamczyk, Sora Lion - Hardest to Be`, with all nineteen languages mapped to it. The artist
  names come from the game's own Phantom Liberty credits, and the format matches the thirteen
  vanilla Growl FM titles.
- `sounds.json`, an AudioXL manifest declaring the bank. It carries an empty `sounds` array,
  because AudioXL returns before its banks loop for a manifest with no `sounds` key.

### Notes
- The source is the vocal recording from the `mq055_hangouts` playlist. A separate instrumental
  recording exists for the Alex heart-to-heart scene and is not used here.
- `primaryLocKey` is the FNV1a32 of the onscreens secondary key. ArchiveXL registers the entry
  under both hashes, and every vanilla radio track's key fits in 32 bits.
- Verified in game alongside Restore Nebula, which also adds a track to Growl FM. Both appear.
