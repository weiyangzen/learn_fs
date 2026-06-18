# sources/test-tools/strace/src/ioctl_iocdef.c

Tiny compile/generation support file that includes ioctl definitions so build scripts can derive or validate `_IOC_*` constants for the target architecture. It has no runtime state or exported decoder logic. Dependencies are `<linux/ioctl.h>` and the build system that compiles or preprocesses it. Risks are host/target header mismatch and architecture-specific ioctl encoding differences. Test signals are successful generation/build on each supported architecture and correct `_IOC` formatting in `ioctl.c`.
