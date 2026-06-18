# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inouparm.c

Level 1 dummy implementation for user-parameter setting.

Key behavior:
- Includes `ghost.h` and `icontext.h`.
- Defines `set_user_params`.
- Ignores the parameter dictionary and returns success.

Research notes:
- This is the `nousparm` fallback in `int.mak`; the Level 2 `usparam` feature replaces it with `zusparam.c`.
