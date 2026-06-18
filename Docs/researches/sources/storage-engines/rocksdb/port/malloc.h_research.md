# Research: sources/storage-engines/rocksdb/port/malloc.h

## Purpose
This header conditionally includes platform malloc headers needed for `malloc_usable_size`-style APIs. It keeps malloc header selection behind RocksDB build macros so most builds avoid non-portable declarations.

## Important APIs, Types, And Functions
The file does not define its own functions or types. If `ROCKSDB_MALLOC_USABLE_SIZE` is defined, it includes `<malloc_np.h>` on FreeBSD (`OS_FREEBSD`) and `<malloc.h>` elsewhere.

## Control Flow
All behavior is preprocessor-driven. Builds that do not opt into `ROCKSDB_MALLOC_USABLE_SIZE` get only the include guard and no system malloc declarations.

## State And Persistence Behavior
There is no runtime state or persistence. The header only affects declaration availability for consumers that query allocator usable sizes.

## Dependencies And Integration Points
Consumers are memory accounting or allocation-size code paths that need `malloc_usable_size` or equivalent declarations. The header depends on build macros selecting both feature use and FreeBSD-specific header naming.

## Risks And Edge Cases
`malloc_usable_size` is non-standard and allocator-specific. Including the wrong header for a platform can break compilation, while enabling the feature with an allocator that does not support the expected API can break builds or runtime assumptions. Keeping this header minimal reduces cross-platform exposure.

## Test Signals
Build coverage with `ROCKSDB_MALLOC_USABLE_SIZE` enabled and disabled is the main signal. Runtime memory-accounting tests should tolerate feature absence and validate reported usable sizes only on supported allocator/platform combinations.
