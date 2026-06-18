<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/watchdog_ioctl.c -->
# sources/test-tools/strace/src/watchdog_ioctl.c

Purpose: Watchdog ioctl decoder for support/status/timeout/pretimeout/timeleft/setoptions/keepalive commands, including `watchdog_info` and option flag tables.

Important APIs/types/functions:
- Helper functions include `watchdog_ioctl`
- Direct includes: `"defs.h"`, `<linux/watchdog.h>`, `"xlat/watchdog_ioctl_flags.h"`, `"xlat/watchdog_ioctl_setoptions.h"`, `"xlat/watchdog_ioctl_cmds.h"`
- Xlat tables consumed: `watchdog_ioctl_flags`, `watchdog_ioctl_setoptions`, `watchdog_ioctl_cmds`
- Local/exported macros: `XLAT_MACROS_ONLY`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `WDIOC_GETSUPPORT`, `WDIOC_GETSTATUS`, `WDIOC_GETBOOTSTATUS`, `WDIOC_GETTEMP`, `WDIOC_GETTIMEOUT`, `WDIOC_GETPRETIMEOUT`, `WDIOC_GETTIMELEFT`, `WDIOC_SETTIMEOUT`, `WDIOC_SETPRETIMEOUT`, `WDIOC_SETOPTIONS`, `WDIOC_KEEPALIVE`

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/watchdog_ioctl.c -->
