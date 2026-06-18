# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/pack.c

Provides all primitive packet cursor serialization/deserialization helpers for CIFS packets. The functions operate directly on `Pkt->pos`, `Pkt->buf`, and `Pkt->eop`.

Packing functions write bytes, little/big-endian integers, 64-bit values, NetBIOS names, DOS date/time, Windows FILETIME, ASCII strings, Unicode strings, and path strings with `/` converted to `\`. Unicode packing enforces the Windows 16-bit codepoint limit.

Unpacking functions read bounded memory, ASCII/Unicode strings, offset-based DFS/transaction strings, big/little-endian integers, DOS date/time, and Windows FILETIME. String reading includes alignment handling and compatibility hacks for Windows Unicode terminators.

`gconv` handles RAP-style converted pointer offsets relative to transaction data. `goff` handles DFS referral string heaps with unaligned Unicode behavior.

Important dependencies: `Pkt` state from `cifs.h`, Plan 9 rune conversion, server flags/caps, and transaction code in `trans.c`, `trans2.c`, and `transnt.c`.

Risk notes: this is a manual cursor parser; it has some bounds checks for numeric reads but string routines rely on protocol shape and pointer validity in places.
