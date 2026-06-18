# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_log.c

This file implements the FUSE logging API. The default log function writes formatted output to `stderr` with `vfprintf`; `fuse_set_log_func` installs a caller callback or resets to default; `fuse_log` formats variadic input and calls the current callback.

When `MULTITHREADED_REFUSE` is enabled, a pthread mutex protects reads/writes of the global log function pointer. Risk is holding the mutex while invoking user-provided log callbacks, which serializes logging but could deadlock if callbacks call back into logging.
