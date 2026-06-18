# File Research: sources/os/bsd/dragonflybsd/sys/sys/file.h

`file.h` defines the kernel file object and file operation vector. It includes common type/fcntl/unistd headers, and under kernel/structure builds includes event, queue, spinlock, namecache, and uio definitions.

`struct fileops` contains read, write, ioctl, kqfilter, stat, close, shutdown, and seek methods. `struct file` tracks active-list linkage, descriptor type, flags, credentials, ops vector, sequential access state, offset, backing data pointers, reference counts, namecache handle, knote list, and DRM-style private data.

The file declares descriptor type constants such as `DTYPE_VNODE`, `DTYPE_SOCKET`, `DTYPE_KQUEUE`, and `DTYPE_DMABUF`, plus kernel helpers for file reference management, open/read/write/stat/mmap/close/shutdown, bad fileops, and system file limits.
