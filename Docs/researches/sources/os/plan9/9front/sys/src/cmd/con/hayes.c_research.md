# File Research: sources/os/plan9/9front/sys/src/cmd/con/hayes.c

Small Hayes-compatible modem dialer. It opens a data device, optionally opens the matching `ctl` file, initializes the modem with `ATZ`, `ATQ0V1E1M1`, and `ATW1`, then dials with pulse or tone via `ATD%c%s`.

Important behavior:
- `readmsg()` polls the file length with `dirfstat()` and reads modem result lines until timeout.
- Known responses classify as `Ok`, `Success`, `Failure`, or `Noise`.
- `getspeed()` parses `CONNECT <baud>` and defaults to 9600.
- `setspeed()` writes baud and modem flow-control commands to the ctl file when present.
- Errors are fatal through `punt()`, which prints `hayes:` messages and exits.
