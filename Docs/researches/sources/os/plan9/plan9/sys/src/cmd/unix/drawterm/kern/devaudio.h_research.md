# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.h

Defines shared audio constants and the backend function contract for `devaudio.c`.

Contents:
- Flags: `Fmono`, `Fin`, `Fout`.
- Volume IDs: `Vaudio`, `Vsynth`, `Vcd`, `Vline`, `Vmic`, `Vspeaker`, `Vtreb`, `Vbass`, `Vspeed`, `Vpcm`, and `Nvol`.
- Backend prototypes for open, close, read, write, get volume, and set volume.

Role:
- Separates the Plan 9 `#A` device implementation from host-specific audio implementations such as `devaudio-unix.c`.
