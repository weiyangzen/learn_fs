# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.h

Declares buffered stream state and BWBlockSort encode/decode state. The shared state contains `BlockSize`, allocated buffer, filling flag, current block size, and position.

The BWBlockSort state adds an `offsets` allocation and encode/decode fields for block length, original index, and current decode index. It exposes encode/decode templates and GC descriptors.

Dependencies are `scommon.h` and `strimpl.h`. This is block compression stream support.
