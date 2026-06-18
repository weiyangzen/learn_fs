# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_exec/pam_exec.c

PAM module that executes an external command for every PAM service hook. `_pam_exec` requires at least one argv element, builds a child environment from the PAM environment plus selected PAM items, then uses `vfork` and `execve`.

It distinguishes exec failure from nonzero child exit using a volatile child error variable, frees the environment in the parent, waits for completion, logs fork/wait/exec/signal/status failures, and returns `PAM_SUCCESS` only for normal zero exit.
