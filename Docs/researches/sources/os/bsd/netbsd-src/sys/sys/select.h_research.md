# File Research: sources/os/bsd/netbsd-src/sys/sys/select.h

Read completely: 78 lines.

This header exposes `select` and `pselect` interfaces and kernel select/poll support hooks. Userland gets versioned `pselect` and `select` prototypes, while kernel code gets `selcommon`, `selrecord`, knote registration/removal, `selnotify`, per-CPU select init, and `selinfo` init/destroy.

Important interactions: kernel consumers include `selinfo.h` for wait-state storage and `signal.h` for `sigset_t`. Userland uses `fd_set` from `sys/fd_set.h`.

Risks: select readiness notification depends on callers maintaining `struct selinfo` correctly and calling `selnotify` on state transitions.
