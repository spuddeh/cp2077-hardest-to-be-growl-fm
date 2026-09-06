# Hardest to Be on Growl FM

Puts *Hardest to Be* on Growl FM, using the copy of the song the game already ships.

The full vocal recording is `base\sound\soundbanks\mediaǲ143559.wem`. It sits in the
apartment hangout's music playlist, `mq055_hangouts`, and no radio station touches it - none of
that playlist's seven tracks is used by any station.

A separate instrumental recording, `528262674.wem`, exists for the Alex heart-to-heart scene. Only
about seven seconds of it are used: the file is 3:27 and the one Wwise node reading it trims 3:09
off the front for an outro sting. That recording is not what this mod plays.

**This mod ships no audio.** It adds the four Wwise objects a radio track needs and points them at
a file the player already has.

## The track title

`archive/pc/mod/HardestToBeGrowlFM.archive` carries one onscreens entry, and the `.xl` beside it
maps every language to that one file. Vanilla leaves a Growl FM title in Latin script for most
languages; Russian and Ukrainian transliterate the artist, so either can be repointed at its own
file without changing anything else.

The entry is authored in `tools/onscreens.json`. To rebuild the archive, convert that to a CR2W
`.json` resource, place it at `mod\hardesttobegrowlfm\localization\onscreens.json` inside a
folder, and pack that folder.

Its `primaryKey` is `0`, which is what makes ArchiveXL derive the keys: it registers the entry
under `FNV1a32` of the secondary key and again under `FNV1a64`. `primaryLocKey` in the `.reds` is
the 64-bit hash and must be recomputed if the key string ever changes.

## Requirements

AudioXL, RED4ext, redscript, Codeware, Phantom Liberty.

## Building the soundbank

```
python tools/make_bank.py <radio.bnk> <cp_music.bnk>     red4ext/plugins/AudioXL/sounds/HardestToBeGrowlFM/hardest_to_be_growl.bnk
```

Both inputs are vanilla banks from `base\sound\soundbanks\`. The generator asserts every field it
reads, so it fails loudly if a game patch moves anything. Pass trailing
`<name> <source_wem> <duration_ms>` triples to put other sources in the bank instead.
