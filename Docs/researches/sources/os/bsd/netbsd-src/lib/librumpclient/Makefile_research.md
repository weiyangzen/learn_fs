# File Research: sources/os/bsd/netbsd-src/lib/librumpclient/Makefile

Read completely: 40 lines.

Builds shared `librumpclient` from `rumpclient.c` and generated `rump_syscalls.c`, installs `rumpclient.h` under `/usr/include/rump`, and includes the `rumpclient.3` manual. It defines `RUMP_CLIENT`, includes the object directory, current directory, and `librumpuser`, and supports externally supplied dependency libraries via `RUMPCLIENT_EXTERNAL_DPLIBS`.

For non-clean/non-obj builds, it creates a `srcsys` symlink to the kernel `sys/sys` headers. It disables full RELRO and suppresses strict-aliasing for generated syscall code and cast-function-type warnings for `rumpclient.c`.
