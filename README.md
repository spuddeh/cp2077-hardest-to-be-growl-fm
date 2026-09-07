# Hardest to Be on Growl FM

Adds *Hardest to Be* to 89.7 Growl FM, so it comes up in rotation like any other track on the
station.

**Nexus:** <https://www.nexusmods.com/cyberpunk2077/mods/33600>

**The mod ships no audio.** The song is already in the game, and the mod points at that copy.

## Requirements

- [AudioXL](https://www.nexusmods.com/cyberpunk2077/mods/23851) - loads the soundbank
- [ArchiveXL](https://www.nexusmods.com/cyberpunk2077/mods/4198) - the track title
- [Codeware](https://www.nexusmods.com/cyberpunk2077/mods/7780)
- [redscript](https://www.nexusmods.com/cyberpunk2077/mods/1511)

[RedLogger](https://www.nexusmods.com/cyberpunk2077/mods/31920) is optional. With it installed the
mod writes what it registered to `r6/logs/mods/`; without it the logging compiles away.

## How it works

A radio station's track list is not a TweakDB record, so no tweak can reach it. It lives in the
game's cooked audio metadata, which this mod patches as it loads - nothing on disk is overwritten.

The soundbank adds the four Wwise objects a radio track needs and points them at the song's
existing audio file. The segment is parented to Growl FM's own playlist, so the track sits at the
same levels as the rest of the station.

Full write-up: [docs/how-it-works.md](docs/how-it-works.md).

## Building the soundbank

```
python tools/make_bank.py <radio.bnk> <cp_music.bnk> \
    red4ext/plugins/AudioXL/sounds/HardestToBeGrowlFM/hardest_to_be_growl.bnk
```

Both inputs are vanilla banks from `base\sound\soundbanks\`. The generator asserts every field it
reads, so a game patch that moves anything fails the build rather than producing a bank that loads
and misbehaves. Pass trailing `<name> <source_wem> <end_trim_ms>` triples to wrap other sources, each
optionally followed by a parent playlist id.

## The track title

`archive/pc/mod/HardestToBeGrowlFM.archive` carries one onscreens entry, and the `.xl` beside it
maps every language to that file. Vanilla leaves a Growl FM title in Latin script for most
languages; Russian and Ukrainian transliterate the artist, so either can be repointed at its own
file without changing anything else.

The entry is authored in `tools/onscreens.json`. Its `primaryKey` is `0`, which is what makes
ArchiveXL derive the keys: it registers the entry under `FNV1a32` of the secondary key and again
under `FNV1a64`. `primaryLocKey` in the `.reds` is the 64-bit hash and must be recomputed if the
key string changes.

## License

Licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE). You may use, modify, and share
this mod and its source for any **noncommercial** purpose, as long as you credit the original
creator. Commercial use, including paid mods or selling, is not permitted. This mirrors the
[mod's Nexus permissions](https://www.nexusmods.com/cyberpunk2077/mods/33600).

## Disclaimer

This mod was developed with the assistance of an LLM. All in-game testing and code validation was
performed by a human. No rogue AIs were permitted through the Blackwall.
