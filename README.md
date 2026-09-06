# Hardest to Be on Growl FM

Puts the song from the Alex heart-to-heart onto Growl FM.

The track is already in the game as `base\sound\soundbanks\media\528262674.wem`, and it is the
music playing on the jukebox in The Moth while Alex says she loves this song. Only about seven
seconds of it are ever used: the file is 3:27, and the one Wwise node that reads it trims 3:09 off
the front to make an outro sting. Nothing plays it whole.

This mod ships no audio. It adds the four Wwise objects a radio track needs and points them at the
file the game already has.

## Requirements

AudioXL, RED4ext, redscript, Codeware, Phantom Liberty.

## Building the soundbank

```
python tools/make_bank.py <radio.bnk> <cp_music.bnk> \
    red4ext/plugins/AudioXL/sounds/HardestToBeGrowlFM/hardest_to_be_growl.bnk
```

Both inputs are vanilla banks from `base\sound\soundbanks\`. The generator asserts every field it
reads, so it fails loudly if a game patch moves anything.
