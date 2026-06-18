# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu.c

Read fully: 731 lines, 14259 bytes. SHA-256 prefix: `5c7f3e5c3c14214c`.

This is drawterm’s normal CPU client connection code. It is nearly identical to `cpu-bl.c`, but defaults `authserver` to `auth` and `system` to `cpu`, making it suitable for local/site configuration.

Main flow:
- `cpumain()` sizes exportfs messages from `/dev/draw`, parses options, determines user/auth/cpu/secstore settings, mounts factotum or fetches secstore data, connects with `rexcall()`, sends command and current directory, waits for remote `FS` and `/` markers, replies `OK`, then calls `exportfs(data, msgsize)`.
- `p9auth()` performs p9any authentication and optional SSL wrapping.
- `p9any()` delegates to factotum when possible, otherwise performs manual p9sk1 ticket exchange.
- `askuser()`, `promptforkey()`, and `sendkey()` collect missing key attributes and add them to factotum.

Risk notes: command building uses repeated `strcat()` into a fixed `MaxStr` buffer, matching historical assumptions rather than robust argv sizing.
