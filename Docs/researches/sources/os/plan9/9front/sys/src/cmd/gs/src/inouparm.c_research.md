# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inouparm.c

Level 1 stub implementation for user-parameter support.

Key behavior:
- Defines `set_user_params`.
- Ignores the supplied parameter dictionary and returns success.

Notable dependencies:
- `ghost.h`.
- `icontext.h` for the `set_user_params` prototype.

Research notes:
- This is the fallback module used when full Level 2 user/system parameter support is not built.
- `int.mak` packages it into `nousparm.dev`; `usparam.dev` replaces it with `zusparam`.
