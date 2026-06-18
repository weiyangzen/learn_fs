# sources/user-network-fs/nfs-ganesha/src/include/os/memstream.h

## Purpose
This cross-platform wrapper exposes platform-dependent memory-stream APIs. It currently includes the FreeBSD implementation header only when `FREEBSD` is defined.

## Important APIs, Types, And Control Flow
The wrapper itself exports no functions. Its only behavior is conditional inclusion of `<os/freebsd/memstream.h>`.

## State And Persistence
There is no state in this wrapper. Any state belongs to the platform memory-stream implementation selected underneath.

## Dependencies And Integration Points
Common code can include `os/memstream.h` without directly branching on platform. Linux relies on libc's native declarations elsewhere, while FreeBSD gets compatibility declarations.

## Risks And Test Signals
The risk is missing declarations on non-Linux/non-FreeBSD platforms or macro mis-detection. Build tests should include modules using memory streams on FreeBSD and Linux, and functional tests should verify buffer ownership and close semantics where compatibility implementations are used.
