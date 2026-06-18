# File Research: sources/os/bsd/dragonflybsd/sys/sys/_termios.h

Read completely: 236 lines.

This header defines terminal control constants and `struct termios`.

Key contents:
- Control character indexes such as `VEOF`, `VERASE`, `VINTR`, `VSUSP`, `VMIN`, and `VTIME`, with BSD extensions under visibility guards.
- Input, output, control, and local flag bit definitions.
- Standard speed constants from `B0` through BSD high-speed values.
- Typedefs `tcflag_t`, `cc_t`, and `speed_t`.
- `struct termios` with input/output/control/local flags, control character array, and input/output speeds.
- BSD `CCEQ()` helper.

Security/reliability notes:
- No runtime behavior. Flag values and struct layout are stable user/kernel ABI for tty ioctls and libc termios functions.
