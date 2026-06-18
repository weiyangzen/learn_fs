# File Research: sources/os/bsd/netbsd-src/sys/sys/lockdebug.h

Defines lock debugging operations and macros. It describes lock operation classes, printer callbacks, abort/dismiss/show functions, and when `LOCKDEBUG` is enabled, allocation/free/want/locked/unlocked/barrier/memory-check functions wrapped with function/line metadata. Without `LOCKDEBUG`, macros compile to no-ops or false.

It is kernel/KMEMUSER-only diagnostic infrastructure. Risks include relying on debug-only checks in production paths, ensuring locks register/free correctly, and avoiding stale lockdebug metadata for freed memory.
