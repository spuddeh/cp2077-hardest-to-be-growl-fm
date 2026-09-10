# Features

## Implemented

- *Hardest to Be* plays on Growl FM in full, streamed from the game's own audio. The mod ships no
  music.
- The vocal recording is used, the one from the hangout playlist. The instrumental cue from the
  Alex scene is a different file and is not played.
- The station shows `P.T. Adamczyk, Sora Lion - Hardest to Be`, in all nineteen languages.
- Coexists with Restore Nebula, which also adds a track to Growl FM, through the optional Restore
  Nebula Compatibility Patch. Without it Restore Nebula's track is lost: Restore Nebula only listens for the
  station data finishing its load, and this mod's read at script start happens first. The patch
  adds Restore Nebula's row itself, once, and only when Restore Nebula is installed.
- The track sits at Growl FM's own level and fades with distance like every other song, because the
  segment carries the station's broadcast sends, bus and dry Volume rather than a tuned trim.

## Planned

- Russian and Ukrainian transliterate a Latin-script artist name in vanilla, and this ships the
  Latin string to every language. A native speaker could supply either.
- The same technique fits any shipped `.wem`. The other six tracks in the hangout playlist are
  already on stations, so there is nothing else in that playlist to restore.
