# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.cc

Purpose: implements the `XrdOucSHA3` SHA-3 and SHAKE primitives, adapted from tiny_sha3, including Keccak-f[1600], fixed-length SHA3 digests, and extensible-output SHAKE reads.

Important APIs, types, and functions: `sha3_keccakf()` is the 24-round permutation; `Calc()` performs one-shot hashing; `Init()`, `Update()`, and `Final()` implement streaming SHA3; `shake_xof()` and `SHAKE_Out()` implement SHAKE output after the same absorb phase.

Control flow: `Init()` clears the 1600-bit state and computes the rate from digest length. `Update()` XORs input bytes into the state and permutes when the rate fills. `Final()` applies SHA3 padding bytes `0x06` and `0x80`, permutes once, and copies `mdlen` bytes. `SHAKE_Out()` lazily applies SHAKE padding `0x1F` on first output, then streams bytes and permutes on rate boundaries.

State and persistence: all state lives in caller-provided `sha3_ctx_t`. The one-shot API uses a stack context. No heap state, globals, locks, or persistence are used. Big-endian platforms perform explicit byte-order conversion around the permutation.

Dependencies and integration points: depends on `XrdOucSHA3.hh`, fixed-width integer types, compiler byte-order macros, and callers needing checksums or extendable pseudo-random output without OpenSSL.

Risks and test signals: there is no validation that `mdlen` is one of the documented enum values, so unsupported rates could corrupt the context contract. `Final()` is terminal for SHA3 but does not mark the context finalized. Tests should use FIPS 202 vectors for all SHA3 lengths, SHAKE128/SHAKE256 vectors across repeated `SHAKE_Out()` calls, empty input, multi-update equivalence, and big-endian builds if supported.
