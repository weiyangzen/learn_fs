# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/class.h

`class.h` defines the kernel scheduler class switch interface. It groups class-manager operations and per-thread operations into `classfuncs_t`, with functions for class admin, parameter conversion, entering/exiting classes, fork/exit, sleep/wakeup, preemption, swap, tick, nice/priority changes, and process-group handling.

It defines `sclass_t`, scheduler load/install state macros, kernel globals for class tables and ids, loader/lookup/parameter helpers, and many `CL_*` dispatch macros used by core scheduling code.
