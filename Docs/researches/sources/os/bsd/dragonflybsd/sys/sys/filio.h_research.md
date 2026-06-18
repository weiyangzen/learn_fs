# File Research: sources/os/bsd/dragonflybsd/sys/sys/filio.h

`filio.h` defines generic file-descriptor ioctl commands. It includes `ioccom.h`.

It declares `struct fiodname_args` for device-name lookup by file descriptor and defines ioctls for close-on-exec manipulation, readable byte count, nonblocking mode, async mode, signal owner get/set, descriptor type, starting block number, descriptor name, and SEEK_DATA/SEEK_HOLE-style hole/data seeking.

This is a small public ioctl ABI shared by many descriptor-like kernel objects.
