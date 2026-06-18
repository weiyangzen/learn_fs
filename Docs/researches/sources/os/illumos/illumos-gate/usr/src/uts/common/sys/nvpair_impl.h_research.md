# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair_impl.h

## Purpose

`nvpair_impl.h` exposes internal nvpair/nvlist implementation structures for information and debugging. It is not a stable public implementation contract.

## Main Interfaces

`i_nvp_t` wraps an `nvpair_t` with implementation linkage. Its union ensures 64-bit alignment and stores next, previous, and hash-bucket next pointers. Macros expose `nvi_next`, `nvi_prev`, and `nvi_hashtable_next`.

`nvpriv_t` stores the private state behind an unpacked nvlist: linked-list head, last pair, current walker pair, allocator, internal state flags, hash table pointer, bucket count, and entry count.

## Runtime Use

The nvpair implementation uses these structures to manage ordered iteration and faster lookup through a hash table. Debuggers and low-level implementation code can inspect them.

## Dependencies

Includes `sys/nvpair.h`.

## Risks and Invariants

The header explicitly says these structures may change. External code should not depend on their layout for ABI stability.

`i_nvp_t` embeds `nvpair_t` after link fields; any code converting between public and private pair pointers must use implementation-approved helpers or known layout carefully.
