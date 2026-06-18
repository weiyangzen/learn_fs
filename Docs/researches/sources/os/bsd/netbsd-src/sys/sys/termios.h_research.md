# File Research: sources/os/bsd/netbsd-src/sys/sys/termios.h

Read completely: 314 lines.

Defines NetBSD terminal control ABI.

Key elements:
- Defines `c_cc[]` control character indexes including POSIX and NetBSD extensions.
- Defines input, output, control, and local mode flags for terminal processing and hardware flow control.
- Defines `tcflag_t`, `cc_t`, `speed_t`, and `struct termios`.
- Defines `tcsetattr` action constants, standard baud rates, and NetBSD extended speeds.
- Userland prototypes include `cfgetispeed`, `cfsetospeed`, `tcgetattr`, `tcsetattr`, `tcdrain`, `tcflow`, `tcflush`, `tcsendbreak`, `tcgetsid`, `cfmakeraw`, and `cfsetspeed`.
- Includes `sys/ttycom.h` for non-obsolete tty ioctls and `struct winsize`.
- Exposes `tcgetwinsize` and `tcsetwinsize`.

Risks and notes:
- `struct termios`, flag values, speed constants, and control indexes are user/kernel ABI.
- Feature-test guards control namespace exposure; broadening visibility can break strict POSIX builds.
