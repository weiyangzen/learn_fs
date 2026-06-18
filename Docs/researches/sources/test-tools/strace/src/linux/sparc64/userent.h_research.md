# sources/test-tools/strace/src/linux/sparc64/userent.h

## Purpose
Defines SPARC64-specific `struct user` offset names for ptrace/user area decoding, then includes the shared `userent0.h` table. It feeds strace's `ptrace` decoder when printing offsets used by `PTRACE_PEEKUSER`, `PTRACE_POKEUSER`, and similar requests.

## Important APIs, Types, and Functions
Uses `XLAT_UOFF(...)` entries for `u_tsize`, `u_dsize`, `u_ssize`, `signal`, `magic`, and `u_comm`. The macro expands into architecture-specific xlat entries expected by `ptrace.c`.

## Control Flow and Integration
There is no runtime branching. The header is included in the generated user-offset xlat table for the SPARC64 Linux port. `#include "userent0.h"` appends common or generated offsets after the SPARC64-specific user-structure fields.

## State and Persistence
No mutable state. The result is static metadata for printing user-area offsets.

## Dependencies
Depends on `XLAT_UOFF` being defined by the including xlat-generation context and on `userent0.h` existing for the rest of the architecture table.

## Risks
Offsets must match the kernel/user ABI used by strace's build headers. Stale entries make ptrace offset output misleading. Since this is table data, build failures usually catch macro problems, but ABI drift may only show up in ptrace decoding tests.

## Test Signals
Exercise `ptrace` decoding with user-area offsets and verify names appear for the listed SPARC64 fields. Regeneration of xlat tables and a SPARC64 build are the strongest compile-time signals.
