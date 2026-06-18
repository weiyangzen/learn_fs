# File Research: sources/os/bsd/netbsd-src/sys/sys/rnd.h

Read completely: 52 lines.

This kernel-only header declares the core random-device entry points. It defines minor numbers for blocking `/dev/random` and nonblocking/random-generating `/dev/urandom`, and declares `rnd_init`, `rnd_init_softint`, `rnd_seed`, and `rnd_system_ioctl`.

Risks: the header is small, but it sits on the randomness initialization and ioctl boundary. Correct consumers must include the richer source/ioctl headers for source registration or userspace control structs.
