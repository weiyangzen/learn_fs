# sources/test-tools/strace/src/term.c

Purpose: ioctl decoder for terminal/TTY command arguments and command-number disambiguation.

Important APIs/types/functions: `term_ioctl`, `term_ioctl_decode_command_number`, `decode_termios2`, `decode_termios`, `decode_termio`, `decode_winsize`, `decode_ttysize`, `decode_modem_flags`, `decode_oflag`, `decode_cflag`, and numerous terminal xlat tables.

Control flow: `term_ioctl` switches on ioctl code. Output ioctls (`TCGETS`, `TIOCGWINSZ`, etc.) defer decoding until exit; setter ioctls decode on entry. Termios decoders print flag fields and, unless abbreviated, line discipline, control characters, and speed fields. Direct numeric commands print decoded values or integers. `term_ioctl_decode_command_number` resolves overlapping TTY/sound command numbers by checking character-device major ranges.

State and persistence behavior: stateless; reads pointed terminal structs or integers from tracee memory.

Dependencies and integration points: called by ioctl dispatch; depends on kernel `<linux/termios.h>`, fd metadata (`struct finfo`), and generated terminal xlat tables.

Risks: libc termios layout is intentionally avoided. Architecture differences in `NCCS`, optional `termios2`, and overlapping ioctl numbers are main compatibility risks.

Test signals: get/set termios and termio, abbreviated and verbose output, winsize/ttysize, modem flag get/set, direct `TCXONC`/`TCFLSH`, int pointer ioctls, `TIOCSTI`, no-arg ioctls, and overlapping command numbers on TTY vs non-TTY fds.
