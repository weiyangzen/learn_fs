# File Research: sources/teaching/xv6-public/file.h

Defines kernel file, inode, and device switch structures.

Contents:
- `struct file`: type, ref count, readability/writability, pipe pointer, inode pointer, and offset.
- `struct inode`: in-memory inode cache entry with ref count, sleeplock, validity, disk metadata copy, and direct/indirect block addresses.
- `struct devsw`: major-device read/write operations.
- External `devsw[]` and `CONSOLE` major number.

Role:
- Shared contract among file descriptor, filesystem, pipe, and device layers.
