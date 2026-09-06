# Changelog

## [0.1.0] - Unreleased

### Added
- `hardest_to_be_growl.bnk`, built by `tools/make_bank.py`: a MusicTrack over
  `base\sound\soundbanks\media\528262674.wem`, a MusicSegment holding it, and an Event with a Play
  action. The segment and track are cloned from `mus_radio_12_afterlife`, so every field the
  generator does not touch already carries a Growl FM track's mix. The segment's parent is Growl
  FM's own playlist, `375417660`.
- `HardestToBeGrowlFM.reds`: appends the event to `eventsmetadata.json` with the source's real
  length, and appends an `audioRadioTrack` row plus the station entry to
  `cooked_metadata.audio_metadata`. Both patches are idempotent.
- `sounds.json`, an AudioXL manifest declaring the bank. It carries an empty `sounds` array
  because AudioXL skips its banks loop for a manifest that has no `sounds` key.

### Notes
- The track title uses `UI-Credits-HARDEST_TO_BE` as a placeholder LocKey.
