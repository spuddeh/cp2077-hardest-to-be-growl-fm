# Restore Nebula Compatibility Patch (optional file)

Puts Restore Nebula's track on Growl FM when this mod, RadioXL, or any other mod
that reads the station data at script start is installed beside it.

Restore Nebula 1.04 adds its track only when it hears the station data finish loading. A resource
another mod has already asked for is not announced again, so with an early reader present the
track is never added. This file reads the resources directly and adds the row itself, checking
first so it never adds twice, and doing nothing when Restore Nebula is not installed. The audio,
the title and the rest of the mod remain Restore Nebula's.

Verified in game beside RadioXL and this mod's main file: Growl FM carries all
fifteen tracks and Nebula plays.

Ships as its own zip: `optional-files/restore-nebula-compatibility-patch/r6` staged as `r6`. Remove it once Restore
Nebula carries the fix.
