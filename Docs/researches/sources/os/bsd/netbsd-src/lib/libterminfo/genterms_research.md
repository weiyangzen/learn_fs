# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genterms

Shell generator for embedded compiled terminal descriptions.

Key responsibilities:
- Calls `tic -Sx` against the source terminfo database.
- Emits C source for built-in terminal entries:
  - `ansi`
  - `dumb`
  - `vt100`
  - `vt220`
  - `wsvt25`
  - `xterm`

Role in subsystem:
- Provides fallback terminal descriptions for environments without an accessible terminfo database, especially small or recovery-style builds.
