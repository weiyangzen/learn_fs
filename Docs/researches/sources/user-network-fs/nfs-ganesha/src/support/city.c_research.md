<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city.c -->
# sources/user-network-fs/nfs-ganesha/src/support/city.c

## Purpose
This file is a C port of Google's CityHash family. It provides fast non-cryptographic 64-bit and 128-bit hashes, plus optional SSE4.2 CRC-accelerated variants for longer buffers.

## Important APIs, Types, and Functions
Public functions include `CityHash64`, `CityHash64WithSeed`, `CityHash64WithSeeds`, `WeakHashLen32WithSeeds`, `CityHash128`, `CityHash128WithSeed`, and, under `__SSE4_2__`, `CityHashCrc256`, `CityHashCrc128`, and `CityHashCrc128WithSeed`. Internal helpers include endian-safe `UNALIGNED_LOAD64/32`, `Fetch64/32`, `Hash128to64`, `Rotate`, `ShiftMix`, `HashLen0to16`, `HashLen17to32`, `HashLen33to64`, and `CityMurmur`.

## Control Flow
`CityHash64` dispatches by input length: specialized paths for 0-16, 17-32, 33-64, and a 64-byte chunk loop for longer strings. Seeded variants hash the base output with seed values. `CityHash128` seeds from the first 8 or 16 bytes when available, then delegates to `CityHash128WithSeed`; the latter uses `CityMurmur` for inputs under 128 bytes and an unrolled 128-byte loop plus tail processing for larger inputs. CRC variants use `_mm_crc32_u64` in 240-byte chunks and fall back to padded short-buffer handling for inputs under 240 bytes.

## State and Persistence Behavior
All functions are pure with respect to process state and operate on caller-provided memory. There is no allocation, locking, or persistence.

## Dependencies and Integration Points
The file depends on `city.h`, `misc/portable.h`, endian macros from configuration, and optionally `citycrc.h` plus `<nmmintrin.h>` for SSE4.2. The `support/CMakeLists.txt` builds it into the `hash` object library for use anywhere NFS-Ganesha needs stable non-cryptographic hashes.

## Risks and Test Signals
Risks include non-cryptographic misuse, architecture-specific behavior if endian or unaligned-load assumptions regress, signed `long` use in `CityMurmur` for very large `size_t` lengths, and optional CRC APIs only existing in SSE4.2 builds. Test signals are `city-test.c` known-answer vectors, builds under big-endian and little-endian configurations, sanitizer runs for boundary lengths 0, 1, 16, 17, 32, 33, 64, 65, 127, 128, 239, and 240, and comparison against upstream CityHash outputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city.c -->
