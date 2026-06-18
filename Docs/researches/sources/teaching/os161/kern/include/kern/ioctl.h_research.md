# File Research: sources/teaching/os161/kern/include/kern/ioctl.h

Placeholder for ioctl operation codes.

Contents:
- Include guard only; no ioctl codes are currently defined.

Relevance:
- SFS and semfs implement vnode ioctl by returning `EINVAL`.
- Device abstraction still exposes an ioctl operation slot.
