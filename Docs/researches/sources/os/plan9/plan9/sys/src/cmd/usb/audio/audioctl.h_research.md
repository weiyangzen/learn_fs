# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.h

Read fully: 29 lines, 618 bytes. SHA-256 prefix: `ce38668e176dfafd`.

This header defines playback/record indexes, `Undef`, `Audiocontrol`, control globals, and control helper prototypes.

`Audiocontrol` records a control name, readability/settability, channel bitmap, cached master/per-channel values, and min/max/step bounds. The header also declares unit IDs for endpoints, interfaces, feature/selector/mixer units, and HID button endpoint.

Integration: shared by `audio.c`, `audioctl.c`, `audiofs.c`, and `audiosub.c`; also registers `%A` formatting for `Audiocontrol`.

Risk notes: value arrays are fixed at 8 entries and depend on channel bitmap interpretation used throughout the driver.
