# File Research: sources/os/bsd/netbsd-src/sys/sys/memfd.h

Defines the kernel `struct memfd` backing `memfd_create`. It stores a name, UVM object pointer, size, seals, and birth/access/modify timestamps.

Filesystem relevance is direct: memfd represents anonymous file-like memory objects with seal state and metadata. Risks include seal enforcement, UVM object lifetime, size synchronization, and timestamp updates across file operations.
