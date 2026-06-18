# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_log.h

This public header declares the FUSE 3.7-style logging API exported by ReFUSE. It defines `enum fuse_log_level`, the `fuse_log_func_t` callback type, `fuse_set_log_func`, and printf-checked `fuse_log`.

Integration points: implemented by `refuse_log.c` and included by consumers through the broader FUSE headers. ABI risk is low, but callback signature and `va_list` lifetime are part of the public contract.
