# File Research: sources/os/bsd/netbsd-src/sys/sys/wait.h

Read completely: 217 lines.

Defines process wait status encoding, wait option bits, compatibility `union wait`, and userland wait-family prototypes.

Status model:
- `WIFSTOPPED`, `WIFCONTINUED`, `WSTOPSIG`, `WIFSIGNALED`, `WTERMSIG`, `WIFEXITED`, and `WEXITSTATUS` decode the integer wait status.
- NetBSD/XOpen/kernel-visible additions include `WCOREFLAG`, `WCOREDUMP`, `W_EXITCODE`, `W_STOPCODE`, and `W_CONTCODE`.
- `_WCONTINUED` uses `0xffffU`; stopped status uses low 7 bits equal to `0177`.

Options:
- POSIX options include `WNOHANG`, `WSTOPPED`/`WUNTRACED`, `WCONTINUED`, `WEXITED`, and `WNOWAIT`.
- NetBSD options include `WALTSIG`, `WALLSIG`, `WTRAPPED`, and `WNOZOMBIE`.
- Linux clone compatibility aliases map `__WCLONE` and `__WALL` to NetBSD alternate/all-signal options.
- Kernel option masks define selectable and all valid options.

Compatibility/user API:
- `WAIT_ANY` and `WAIT_MYPGRP` expose special pid values.
- Deprecated `union wait` maps status bits with endian-specific bitfields.
- Userland prototypes expose `wait`, `waitpid`, `waitid`, and NetBSD/XOpen `wait3`, `wait4`, `wait6` with symbol renames for older ABI variants.

Risks and notes:
- The file is ABI-sensitive: bit layout differs by endian for deprecated `union wait`, while macro decoding uses integer status.
- Feature-test macros control which legacy or extension names are visible.
