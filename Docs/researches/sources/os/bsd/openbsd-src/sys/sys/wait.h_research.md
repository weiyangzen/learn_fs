# File Research: sources/os/bsd/openbsd-src/sys/sys/wait.h

Defines wait status encoding macros and wait option bits. It exposes `WIFSTOPPED`, `WSTOPSIG`, `WIFSIGNALED`, `WTERMSIG`, `WIFEXITED`, `WEXITSTATUS`, `WIFCONTINUED`, and XPG core-dump/status construction helpers.

Options include `WNOHANG`, `WUNTRACED`, `WCONTINUED`, POSIX `WEXITED`, `WSTOPPED`, `WNOWAIT`, and `WTRAPPED`; POSIX visibility also defines `idtype_t`. Userland prototypes include `wait`, `waitpid`, `waitid`, and BSD `wait3`/`wait4`.
