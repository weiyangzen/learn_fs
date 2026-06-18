# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pkp_hash.h

## Purpose
Declares a Pearson-style string hash used by kernel code.

## Main Interfaces
- `PKP_HASH_SIZE`: hash table size of 256.
- `pkp_tab_hash(char *, int)`: computes a hash over a character buffer and length.

## Dependencies And Relationships
Includes `sys/types.h`. The comment references Pearson’s string hash algorithm from CACM.

## Research Notes
This is a small declaration header; the hash table or algorithm implementation lives elsewhere.
