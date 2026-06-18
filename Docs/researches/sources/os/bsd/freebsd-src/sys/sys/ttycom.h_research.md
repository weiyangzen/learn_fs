# File Research: sources/os/bsd/freebsd-src/sys/sys/ttycom.h

TTY ioctl ABI header.

Key responsibilities:
- Defines ioctl numbers for exclusive mode, pty number, buffer flush, termios get/set, line discipline get/set, pty master validation, drain wait, input timestamp, drain, pty signal/external/user-control modes, controlling tty, console redirection, session ID, status, window size, modem control, output start/stop, packet mode, simulated input, output queue count, process group, DTR, and break control.
- Defines modem bit constants and aliases.
- Defines packet-mode event bits.
- Defines line discipline numbers for termios, SLIP, PPP, netgraph, and Bluetooth H4.

Dependencies:
- Includes `sys/ioccom.h` and `_winsize`.

Notable risks:
- Numeric ioctl slots preserve historical gaps and conflicts with tun/tap; changing values would break userland and driver ABI.
- `TIOCSTI`, console control, process-group, and pty signal ioctls have security-sensitive implementations outside this header.
