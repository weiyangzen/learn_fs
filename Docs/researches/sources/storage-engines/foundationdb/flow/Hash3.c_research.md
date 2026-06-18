# sources/storage-engines/foundationdb/flow/Hash3.c

## Purpose
Provides Bob Jenkins lookup3 non-cryptographic 32-bit hashing routines for words and byte arrays, including endian/alignment fast paths and optional self-tests.

## Important APIs, Types, And Functions
Exports `hashword()`, `hashword2()`, `hashlittle()`, `hashlittle2()`, and `hashbig()`. Internal macros `rot`, `mix`, and `final` implement reversible mixing and final avalanche-style mixing. `HASH_LITTLE_ENDIAN` and `HASH_BIG_ENDIAN` select architecture paths.

## Control Flow
Word hashing initializes `a/b/c` with `0xdeadbeef`, length, and seed(s), mixes groups of three 32-bit words, handles fall-through tails, and returns or writes final hash values. Byte hashing selects aligned 32-bit little-endian, aligned 16-bit little-endian, byte-wise, or big-endian paths, processes 12-byte blocks, then finalizes the remaining tail. Sanitizer/Valgrind builds avoid deliberate masked over-reads.

## State And Persistence Behavior
The functions are stateless and deterministic for a given input, seed, architecture mode, and function. No allocation or I/O occurs unless `SELF_TEST` is compiled.

## Dependencies And Integration Points
Uses C standard headers and platform endian headers. It integrates anywhere Flow needs stable lookup hashes, hash-table seeds, or compact IDs where cryptographic strength is not required.

## Risks And Edge Cases
The header comment explicitly rejects cryptographic use. Fast aligned tail handling can read past logical end when not under Valgrind/ASAN, relying on word-boundary safety. Cross-endian output differences are intentional between `hashlittle` and `hashbig`; callers needing persisted compatibility must choose carefully. Fall-through switches must remain warning-compatible.

## Test Signals
`SELF_TEST` contains timing, avalanche, alignment-boundary, zero-length, and known-vector drivers, but it is disabled by default. Practical signals include sanitizer builds selecting safe paths and any downstream tests that depend on stable hash outputs.
