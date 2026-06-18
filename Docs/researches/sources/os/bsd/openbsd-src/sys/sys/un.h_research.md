# File Research: sources/os/bsd/openbsd-src/sys/sys/un.h

Defines UNIX-domain socket address ABI. `struct sockaddr_un` has a length byte excluding NUL, address family, and 104-byte path.

BSD userland gets `SUN_LEN(su)`, computing the actual initialized address length from the path string. Kernel code only needs the structure definition here.
