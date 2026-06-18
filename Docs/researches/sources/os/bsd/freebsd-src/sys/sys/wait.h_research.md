# File Research: sources/os/bsd/freebsd-src/sys/sys/wait.h

User/kernel wait-status ABI header for `wait`, `waitpid`, `wait3`, `wait4`, `wait6`, and `waitid`.

Key content:
- Defines wait status inspection macros: `WIFSTOPPED`, `WSTOPSIG`, `WIFSIGNALED`, `WTERMSIG`, `WIFEXITED`, `WEXITSTATUS`, `WIFCONTINUED`, and BSD-visible `WCOREDUMP`.
- Defines status construction helpers `W_EXITCODE`, `W_STOPCODE`, and kernel-facing `KW_EXITCODE`, which clamps process return codes to the low 8 bits.
- Defines wait option bits: `WNOHANG`, `WUNTRACED`/`WSTOPPED`, `WCONTINUED`, `WNOWAIT`, `WEXITED`, `WTRAPPED`, and BSD-visible `WLINUXCLONE`.
- Defines `idtype_t` selector values for `waitid()`/`wait6()` style APIs, including process, parent process, process group, session, user/group, all processes, LWP, task, project, pool, jail/zone, contract, CPU, and processor set IDs.
- Defines BSD special pid tokens `WAIT_ANY` and `WAIT_MYPGRP`.
- Exposes userland prototypes for wait-family calls when not compiling the kernel.

Research relevance:
- Not filesystem-specific, but part of the FreeBSD public ABI surface in this group.
- Useful when studying syscall ABI style, process status encoding, and compatibility-visible constants.
