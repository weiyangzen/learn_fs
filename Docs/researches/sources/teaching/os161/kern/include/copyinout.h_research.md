# File Research: sources/teaching/os161/kern/include/copyinout.h

Declares safe copy helpers between user and kernel address spaces.

APIs:
- `copyin`, `copyout` for fixed-length buffers.
- `copyinstr`, `copyoutstr` for null-terminated strings with returned length.
- Errors include `EFAULT` and `ENAMETOOLONG`.

Relevance:
- Filesystem syscalls and VFS layers use these helpers around pathnames, buffers, and stat data before reaching vnode operations.
