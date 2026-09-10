# Changelog

## [Unreleased]

### Added

- Optional file `Nebula Loader` (`optional-files/nebula-loader`, artifact `nebula-loader`, its own
  version 1.0.0): a standalone service that adds Restore Nebula's event row, track and title from
  the depot-token path with add-once checks, guarded by `ResourceExists` on a file only Restore
  Nebula's archive provides. Restore Nebula 1.04 listens for `Resource/Loaded` only and is never
  told about a resource this mod or NRF loads at script start.

## [1.0.1] - 2026-09-09

### Fixed
- The track played about 15 dB above the rest of Growl FM, and did not attenuate with distance. A
  station playlist mutes its own dry output at `Volume -96 dB` and is heard only through its pair of
  CPR Voice Broadcast Send effects, and a segment defined in this bank inherits none of that from a
  parent in `radio.bnk`. The clone was playing dry, on the raw music path, at the source file's own
  level. `make_bank.py` now reads the parent playlist's effect chain, bus and Volume and writes them
  onto the cloned segment, so the level comes from the station's own send trim rather than a number.
  Measured at one world device across a continuous capture: -21.2 LUFS against vanilla neighbours at
  -19.5 to -24.4, where it had been -10.9 and clipping at +0.7 dBFS true peak.

### Notes
- `parse_station` and `adopt_station` handle the record growing: the effect block moves
  `OverrideBusId` and the property bundle, so no offset past it is fixed.

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
