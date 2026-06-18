# File Research: sources/os/plan9/plan9/sys/src/9/rb/devarch.c

RouterBOARD architecture device `#P`, exposing CPU/timer/MMU/FP-emulation status and controls.

Key responsibilities:
- Implements dynamic arch-file registration through `addarchfile`.
- Provides Plan 9 device methods for attach, walk, stat, open, read, write, and close.
- Exposes `cputype`, `timebase`, and `archctl`.
- `archctlread` reports CPU MHz, software-TLB hash collisions, kernel/user TLB misses, FP emulator debug status, and optional fault stats.
- `archctlwrite` controls `fpemudebug` when compiled with `FPEMUDEBUG`.

Dependencies:
- Uses Plan 9 dev/net utility functions, command parsing, MIPS timing helpers, and `faultsprint`/`fpemuprint`.

Notable risks:
- `Qmax` is fixed at 16 and files cannot be deleted once added.
- `nsread` is present but not registered.
- Debug command name is replaced with `dummy` unless `FPEMUDEBUG` is enabled.
