# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.c

Classic/Carbon MacOS platform core routines.

Key behavior:
- Provides basic init/exit/termination hooks and a DLL-instance identifier `hwndtext`.
- Implements Mac-oriented time functions using `time`, `GetDateTime`, `SecondsToDate`, and `Microseconds`.
- Provides realtime and usertime approximations.
- Returns no platform error string.
- Stubs persistent cache operations.
- Provides no-op console initialization and display-env lookup.
- Contains older alternate clock implementations for days since January 1, 1980 and nanosecond-style fractions.

Notable dependencies:
- Classic Mac and Carbon headers, `gsdll.h`, `gpcheck.h`, and `gp_mac.h`.

Research notes:
- Several blocks are disabled or legacy, including default library path initialization.
- The active `gp_get_usertime` subtracts a random byte from seconds, apparently to perturb random seeds on very fast systems.
