# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi_impl.h

## Purpose
Provides private implementation declarations for TPI sockfs code and defines the combined allocation object used by normal TPI sockets.

## Key Elements
Defines `sotpi_sonode_t`, embedding a generic `sonode` plus a `sotpi_info_t`; its `so_priv` always points to the embedded `st_info`. Declares internal helpers for TPI capability processing, stream initialization, address allocation and validation, AF_UNIX address translation, stream/socket conversion, ack and connection indication queuing, disconnect indication flushing, protocol mblk allocation, async signal ownership, hook installation, direct send paths, and datagram/service send helpers.

## Dependencies
Includes `sys/socketvar.h` and `fs/sockfs/socktpi.h`, then exposes functions implemented across `socktpi.c` and other sockfs support files.

## Behavior/Risks
This is private linkage glue. The declarations encode locking and ownership assumptions that are visible only in implementations: ack/connection queues are mblk-owned, stream/socket conversion changes observable ioctl behavior, and direct send helpers assume socket state checks were already performed by callers.
