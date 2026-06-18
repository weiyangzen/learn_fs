# File Research: sources/os/bsd/freebsd-src/sys/sys/jaildesc.h

Kernel-only jail descriptor support. `struct jaildesc` associates a file descriptor object with a `struct prison`, maintains the prison’s descriptor list link, a mutex, selinfo for event notification, and flags.

Flags identify removed jails and owning descriptors, where closing the descriptor removes the jail. Lock macros initialize/destroy/lock/unlock `jd_lock`.

APIs find descriptors from fd, allocate descriptors, get/set the associated prison, clean up descriptors for a prison, and deliver knote notifications.
