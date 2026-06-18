# File Research: sources/os/bsd/openbsd-src/sys/sys/sigio.h

Async I/O signal ownership structures.

This header declares `struct sigio_ref` as the stable reference slot embedded by devices and sockets that support `SIGIO`/`SIGURG` ownership. Kernel builds define `struct sigio`, which records whether signals target a process or process group, links into process/group revocation lists, remembers the owning reference slot, credentials, and pgid.

The kernel API initializes, copies, frees, revokes lists, gets ownership, and sets ownership for `FIOASYNC`/`SIOC*PGRP` style behavior. Lock annotations identify `sigio_lock` as the protecting lock.

Filesystem/storage relevance: this is relevant to descriptors whose readiness is exposed through file operations, especially sockets, ttys, fifos, and device vnodes. Regular filesystem files generally do not depend on async signal ownership.
