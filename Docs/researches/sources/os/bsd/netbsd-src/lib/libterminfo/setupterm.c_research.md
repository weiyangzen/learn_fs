# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/setupterm.c

Implements terminal setup for both global and explicit-terminal APIs.

Key responsibilities:
- Provides `use_env`, controlling whether `LINES` and `COLUMNS` override detected dimensions.
- Implements `ti_setupterm`, which:
  - resolves terminal name from argument or `TERM`,
  - allocates a `TERMINAL`,
  - loads capabilities through `_ti_getterm`,
  - rejects generic or hardcopy terminals,
  - records file descriptor and output speed,
  - obtains terminal size via `TIOCGWINSZ`,
  - applies `LINES`/`COLUMNS` overrides.
- Implements `setupterm`, which wraps `ti_setupterm` and installs the result as `cur_term`.

Error behavior:
- If `errret` is `NULL`, failures call `errx(EXIT_FAILURE, ...)`.
- If `errret` is provided, returns `ERR` and stores the terminfo-compatible status code.

Role in subsystem:
- Entry point for initializing runtime terminfo state.
