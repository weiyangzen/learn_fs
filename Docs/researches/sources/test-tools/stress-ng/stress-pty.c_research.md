# sources/test-tools/stress-ng/stress-pty.c research

Purpose: implements `pty`, an OS stressor that opens many pseudoterminal master/slave pairs and exercises terminal attributes, line discipline, queue, packet, and path configuration ioctls.

Important APIs, types, and functions: `stress_pty_info_t` stores follower name plus master/follower fds. `stress_pty()` opens `/dev/ptmx`, calls `ptsname`, `grantpt`, `unlockpt`, opens the slave side, performs a large set of `termios`, `termio`, and `ioctl` operations, then closes all pairs.

Control flow: the stressor allocates an array sized by `pty-max`, synchronizes, then loops opening as many PTYs as possible until resource errors or the configured limit. For each valid pair it reads `/proc` fdinfo, gets and sets terminal attributes, drains/flushes/flows the slave, gets and sets window size, line discipline, queue status, PTY lock/number/packet mode, input/output speeds, optional line discipline cycling, and pathconf values. It closes all descriptors each cycle and increments bogo ops.

State and persistence: only file descriptors and transient kernel PTY state are used. Any changed line discipline is restored to the original value before cleanup when that path runs.

Dependencies and integration: gated by `termios.h` and `ptsname`; optional blocks cover `termio.h` and many platform ioctl constants. It uses stress-ng fdinfo helpers and option parsing. It registers as `CLASS_OS`, `VERIFY_ALWAYS`.

Risks: opening up to 65536 PTYs can hit `EMFILE`, `ENOMEM`, `ENOSPC`, or driver limits; these are expected. Some ioctls may return `EINTR` and are tolerated, while other failures are treated as stressor failures. Line discipline cycling is restricted to instance zero and nonblocking mode because it can be disruptive.

Test signals: resource-limit breaks, ioctl failure logs, bogo count per open/exercise/close cycle, and no leaked fd growth are primary signals.
