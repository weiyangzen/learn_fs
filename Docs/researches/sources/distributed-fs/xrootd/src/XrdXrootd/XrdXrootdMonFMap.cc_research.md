# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFMap.cc

Purpose: implements a small fixed-size slot map that stores active `XrdXrootdFileStats` pointers for periodic file-transfer monitoring.

Important APIs/types/functions: `Init()` allocates and chains slots, `Insert()` takes a free slot and stores a stats pointer, `Free()` returns a slot to the free list, and `Next()` iterates valid slots.

Control flow: the first `Insert()` lazily calls `Init()` if there is no free list. Free slots are marked by setting low-bit `invVal` in the union storage and linked through `cPtr`. `Insert()` pops the head, clears the invalid bit, stores `vPtr`, and returns the slot index. `Free()` validates bounds and current validity, then pushes the slot back to `free`. `Next()` scans forward until it finds a valid slot and advances the caller's cursor.

State and persistence behavior: owns one aligned `fMap` array per map object and a free-list head. No durable state; pointers refer to live file-stat objects owned elsewhere.

Dependencies: `posix_memalign`, `getpagesize`, `XrdSysPlatform`, `XrdXrootdFileStats`, and the declaration in `XrdXrootdMonFMap.hh`.

Integration points: `XrdXrootdMonFile` keeps an array of these maps to register files that need interval transfer records.

Risks: validity marking uses pointer/long punning and assumes pointer alignment leaves the low bit free. `Next()` loops while `slotNum < fmSize-1`, which can skip the final slot. The map itself is not internally synchronized; callers must hold `fmMutex`. Memory is never freed by the destructor.

Test signals: first insert initializes all slots; insert/free/reinsert returns reusable indices; invalid free rejection; iteration sees all active slots including boundary indices; concurrent access only under external lock; full-map insert returns `-1`.
