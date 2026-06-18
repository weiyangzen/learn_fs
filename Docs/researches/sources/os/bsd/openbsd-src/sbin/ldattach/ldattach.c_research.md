# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/ldattach.c

`ldattach.c` attaches tty line disciplines to serial devices, optionally relaying data through a newly allocated pty. Supported disciplines are `nmea`, `msts`, and `endrun`, mapped to kernel line-discipline constants.

The command-line parser handles serial settings for data bits, parity, stop bits, hardware flow control, hangup-on-close, baud rate, timestamp conditions, no-daemon mode, and pty relay mode. It recognizes init-launched execution by parent PID and delays restart after failure when run from init.

After opening the device, it updates termios selectively, sets DTR, attaches the line discipline with `TIOCSETD`, configures timestamping with `TIOCSTSTAMP`, and for supported disciplines forces raw-ish input/output settings. With `-p`, it opens a pty pair, prints the slave path, daemonizes if requested, and relays both directions with `poll()` and `atomicio()`.

Signal handling is minimal: SIGHUP/SIGTERM set a global `dying` flag to exit the relay or suspend loop.
