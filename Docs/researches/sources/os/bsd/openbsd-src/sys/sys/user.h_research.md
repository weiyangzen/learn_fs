# File Research: sources/os/bsd/openbsd-src/sys/sys/user.h

Defines the minimal historical per-process `struct user`, now containing only the machine PCB. It includes machine PCB and resource headers.

The comments preserve the older swapped-process model, but this OpenBSD version is a very small architecture/process context wrapper rather than a broad process metadata store.
