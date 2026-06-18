# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/corectl.h

`corectl.h` defines the `corectl()` system call subcodes, core dump option bits, and content-selection masks for stack, heap, mapping classes, shared memory, CTF, symbols, and debug info. `core_content_t` is a `u_longlong_t`.

It defines refcounted kernel content/path holders and per-zone core globals. Kernel declarations initialize defaults and manage held content/path values; userland declarations expose convenience functions to set/get global, default, and per-process core paths/content/options.
