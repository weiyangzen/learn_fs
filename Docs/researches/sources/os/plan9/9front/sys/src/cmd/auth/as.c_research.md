# File Research: sources/os/plan9/9front/sys/src/cmd/auth/as.c

Run a command as another user on a CPU server using Plan 9 uid capabilities.

Key responsibilities:
- Parses `-d` namespace debug and `-n namespace`.
- Creates a private environment/name space.
- Generates a kernel uid-change capability through `/dev/caphash` and consumes it through `/dev/capuse`.
- Mounts factotum for the new user.
- Builds the target user's namespace and execs the requested command or interactive rc.

Dependencies:
- Uses auth namespace setup from `authcmdlib.h`/auth library and Plan 9 capability devices.

Research notes:
- Intended for hostowner use.
- Relative commands are retried under `/bin`.
