# sources/test-tools/xfstests-bld/fstests-bld/popt/lookup3.c

## Purpose

`lookup3.c` contains Bob Jenkins' public-domain lookup3 non-cryptographic hash implementation, adapted for conditional compilation in the vendored `popt` library. It can provide 32-bit hashes for word arrays, little-endian byte arrays, big-endian byte arrays, and paired 32-bit outputs. The introductory comments state that `jlu32l()` is the common byte-array hash, while `jlu32lpair()` returns two hashes for roughly the cost of one.

The source was read as a complete 969-line C file, including optional self-test code guarded by `_JLU3_SELFTEST`.

## Important APIs, Types, and Functions

The file includes `<stdint.h>` and relies on `size_t`; self-test builds also require standard library declarations for `time()` and `printf()` through the surrounding build configuration or compiler defaults.

Important macros and data objects are:

- `static const union _dbswap endian` detects host byte order at runtime-like compile-unit scope.
- `HASH_LITTLE_ENDIAN` and `HASH_BIG_ENDIAN` inspect the byte layout of `0x11223344`.
- `ROTL32(x, s)` performs 32-bit left rotation unless supplied externally.
- `_JLU3_INIT(h, _size)` seeds the internal state as `0xdeadbeef + size + h`.
- `_JLU3_MIX(a,b,c)` is the reversible 12-byte block mixer.
- `_JLU3_FINAL(a,b,c)` performs final avalanche-style mixing into `c`.

Public hash functions are conditionally emitted:

- `jlu32w(uint32_t h, const uint32_t *k, size_t size)` hashes an array of 32-bit words where `size` is a word count.
- `jlu32l(uint32_t h, const void *key, size_t size)` hashes a byte array using little-endian order where possible.
- `jlu32lpair(const void *key, size_t size, uint32_t *pc, uint32_t *pb)` returns two 32-bit hash values through output parameters seeded by the input values of `*pc` and `*pb`.
- `jlu32b(uint32_t h, const void *key, size_t size)` hashes byte arrays with big-endian-oriented ordering.

Defining `_JLU3_SELFTEST` automatically defines all four hash feature macros and compiles `driver1()`, `driver2()`, `driver3()`, `driver4()`, and `main()`.

## Control Flow

Each hash initializes three 32-bit accumulators `a`, `b`, and `c` from `_JLU3_INIT`; `jlu32lpair()` additionally adds the secondary seed `*pb` into `c`. Null input pointers short-circuit: `jlu32w()` and `jlu32l()` return the initialized `c`, `jlu32lpair()` stores initialized `c` and `b` through its outputs, while `jlu32b()` returns the original seed `h`.

For full blocks, the functions consume 12 bytes or three 32-bit words at a time, add them into `a`, `b`, and `c`, then call `_JLU3_MIX()`. Tail processing is branch-heavy and specialized:

- `jlu32w()` handles up to three remaining words and calls `_JLU3_FINAL()` when at least one word remains.
- `jlu32l()` and `jlu32lpair()` choose among aligned little-endian 32-bit reads, half-aligned little-endian 16-bit reads, or byte-by-byte assembly. The aligned non-`VALGRIND` tails intentionally read a full word and mask unused bytes for speed.
- `jlu32b()` chooses aligned big-endian 32-bit reads when possible, otherwise assembles bytes manually in big-endian order.

After non-empty tail handling, `_JLU3_FINAL()` is applied and `c` is returned as the primary hash. `jlu32lpair()` also returns `b` as the secondary hash. The self-test `main()` runs timing, avalanche, alignment/overread, and zero-length repeated-hash checks, then returns `1`.

## State and Persistence Behavior

The hash functions are deterministic and mostly pure: they read caller-provided memory and return values, with `jlu32lpair()` mutating only `*pc` and `*pb`. The only file-scope state is immutable endian-detection data. There is no allocation, file I/O, caching, or persistent state.

Self-test builds write diagnostics to stdout and use local stack buffers. They do not persist files or modify global state, but their `main()` changes the compilation unit from a library source into a standalone test program.

## Dependencies and Integration Points

The implementation integrates through preprocessor feature macros that select which symbols are compiled. In popt-derived trees, these functions are commonly used by popt's lookup/filter code; the surrounding build may rename symbols or define only the needed `_JLU3_*` feature macros to avoid exporting unused functions.

The code depends on C integer wraparound semantics for `uint32_t`, predictable byte widths for `uint8_t`/`uint16_t`/`uint32_t`, and host behavior for unaligned reads only when alignment checks permit the cast path. The `VALGRIND` macro switches tail code away from deliberate masked overreads so memory-checking builds can run cleanly.

## Risks and Edge Cases

The hash is explicitly not cryptographic. It should not be used for adversarial hash flooding protection, authentication, signatures, or any security boundary where collisions matter. The recommended use is hash table lookup or IDs where a random 32-bit or paired 64-bit collision rate is acceptable.

Endian and alignment paths are performance-sensitive and easy to break. The non-`VALGRIND` aligned tail code deliberately reads past the logical key length but masks unused bytes; this assumes the extra bytes live in the same accessible aligned word. It can still be reported by memory checkers and can be unsafe on unusual memory-mapped boundaries. Strict-aliasing and unaligned-access concerns are mitigated by alignment checks and byte fallbacks but remain important for compiler settings and non-mainstream architectures.

There is an apparent syntax defect in the `VALGRIND` branch of `jlu32l()` at the `case 12` line where `a+=k[0]` is missing a semicolon before `break`; this path only compiles when `VALGRIND` and `_JLU3_jlu32l` are defined. The self-test code uses `time_t` and `printf()` without visible includes in this file, so standalone self-test compilation may need additional includes or permissive compiler settings depending on the surrounding build.

## Test Signals

Core test signals are deterministic hash-vector checks for empty input, one-byte through twelve-byte tails, longer multi-block inputs, null pointer behavior, repeated seeding, and paired-hash output. Platform coverage should exercise little-endian aligned 32-bit reads, little-endian half-aligned reads, byte fallback paths, and big-endian behavior where available.

Memory-safety signals include running with `VALGRIND` defined under Valgrind or sanitizers, testing buffers positioned at the end of an allocation/page, and verifying no bytes beyond the logical key affect the result. Build signals include compiling each conditional API macro combination used by popt, compiling `_JLU3_SELFTEST`, and ensuring the self-test drivers report no avalanche or alignment errors. Integration tests should verify any popt data structure using `jlu32lpair()` remains stable across compiler optimization levels and target architectures.
