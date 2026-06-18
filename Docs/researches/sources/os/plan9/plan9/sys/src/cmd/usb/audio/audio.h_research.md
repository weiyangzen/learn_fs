# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.h

Read fully: 84 lines, 2050 bytes. SHA-256 prefix: `7de4a938c843d06d`.

This header defines USB audio descriptor constants, control IDs, sample format tags, `Audioalt`, capability bits, global driver state, and cross-file function prototypes.

`Audioalt` stores alternate-setting audio capabilities: channel count, resolution, subframe size, continuous/discrete frequency ranges, and flags such as `has_setspeed`, `has_contfreq`, `has_discfreq`, `onefreq`, and `maxpkt_only`.

Integration: shared by all USB audio implementation files. It connects descriptor parsing, control selection, endpoint setup, and the 9P file server.

Risk notes: control IDs mix USB-standard and implementation-defined controls in one enum. Array dimensions and indexes must remain aligned with `audioctl.h` and `controls[2][Ncontrol]`.
