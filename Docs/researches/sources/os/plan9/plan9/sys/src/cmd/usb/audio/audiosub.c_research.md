# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiosub.c

Read fully: 300 lines, 8015 bytes. SHA-256 prefix: `53df19a9efb07f1f`.

This file parses USB audio class-specific interface descriptors and populates driver control/topology state. It names terminal types, tracks playback/record unit IDs, identifies terminals, mixers, selectors, feature units, and streaming format descriptors.

`audio_interface()` switches on interface subclass: audio control descriptors define input/output terminals, mixer/selector/feature units, and available controls; audio streaming descriptors define terminal linkage and format type details. Format descriptors populate `Audioalt` with channels, resolution, subframe size, continuous/discrete frequencies, and capability flags.

Feature-unit parsing marks supported mute/volume/bass/etc. controls as readable/settable for master or per-channel use. Selector and mixer unit IDs are assigned to playback or record based on source unit membership.

Integration: called during `audio.c` descriptor scan before `findalt()` and `getcontrols()`. It writes globals from `audioctl.h`.

Risk notes: topology inference is heuristic and fixed-size (`units[2][8]`). Complex devices with multiple mixers/selectors/features can trigger "Second ..." warnings and overwrite unit IDs.
