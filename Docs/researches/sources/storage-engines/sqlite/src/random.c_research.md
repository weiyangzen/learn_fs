# sources/storage-engines/sqlite/src/random.c

## Purpose
`random.c` implements SQLite's process-wide pseudo-random byte generator. SQLite uses these bytes for internal needs such as random rowids, temporary filenames, and other backend randomness. The generator is based on the RFC 7539 ChaCha20 block function, seeded from the active VFS randomness source on first use, and protected by SQLite's static PRNG mutex in threadsafe builds.

This is not exposed as a cryptographic API contract to applications, but it is security-sensitive because poor randomness can affect filename unpredictability and rowid collision behavior.

## Important APIs, Types, and Functions
`sqlite3_randomness(int N, void *pBuf)` is the public/internal entry point. It fills `pBuf` with `N` bytes, initializes the global PRNG if needed, and resets the generator when called with `N<=0` or `pBuf==NULL`.

`chacha_block(u32 *out, const u32 *in)` implements the 20-round ChaCha block function using the `QR` quarter-round macro and `ROTL()` rotations. It copies the 16-word input state, performs 10 double rounds over columns and diagonals, then adds the original input words into the output words.

The global state is `sqlite3Prng`, a `sqlite3PrngType` containing `s[16]` ChaCha state words, `out[64]` cached output bytes, and `n` remaining cached bytes. With `SQLITE_OMIT_WSD`, the `GLOBAL()` macro locates writable static data at runtime; otherwise the static object is used directly.

When `SQLITE_UNTESTABLE` is not defined, `sqlite3PrngSaveState()` and `sqlite3PrngRestoreState()` copy the PRNG state to/from `sqlite3SavedPrng` for `sqlite3_test_control()` determinism.

## Control Flow
`sqlite3_randomness()` optionally auto-initializes SQLite, obtains `SQLITE_MUTEX_STATIC_PRNG` in threadsafe builds, and treats invalid or non-positive requests as a reset by setting `s[0]=0`. On the next real request, `s[0]==0` triggers initialization.

Initialization writes the ChaCha constants into `s[0..3]`, obtains 44 bytes of entropy from `sqlite3OsRandomness()` into `s[4]` onward when a VFS is available, or zero-fills those words in the unreachable no-VFS case. It then copies `s[12]` into `s[15]`, resets `s[12]` to zero as the block counter, and marks the cached output empty.

For output, the function first consumes any cached bytes from `out`. If the request fits in the cache, it copies from `&out[n-N]`, decrements `n`, and returns. Otherwise it copies remaining cached bytes from the start of `out`, advances the destination, increments `s[12]`, generates a new 64-byte ChaCha block into `out`, sets `n=64`, and repeats. The mutex is held for the entire request so state updates and cached-byte accounting are serialized.

## State and Persistence Behavior
The PRNG state is global to the process or SQLite library instance, not per database connection. It persists between calls until explicitly reset with `sqlite3_randomness(N<=0, NULL/non-NULL)` or restored by test controls. The cached output buffer is consumed from the end for partial reads and from the start when draining the remainder before a new block, so output order depends on `n` accounting.

The initial seed depends on the default VFS returned by `sqlite3_vfs_find(0)` and its `xRandomness` implementation via `sqlite3OsRandomness()`. The code requests 44 seed bytes beyond the 16-byte ChaCha constant. The block counter uses `s[12]` after moving the original seeded word into `s[15]`, preserving all seed material while making room for a counter.

Test save/restore snapshots include state words, cached output bytes, and remaining-byte count. They do not take the PRNG mutex themselves in this file, so callers must use them through the test-control path with appropriate external serialization expectations.

## Dependencies and Integration Points
The file depends on SQLite initialization, the VFS registry/randomness method, static mutex allocation, global writable static data support, and test-control infrastructure. `sqlite3_randomness()` is part of SQLite's public C API and is also used internally by subsystems that need random bytes.

Threading integration is simple but important: in `SQLITE_THREADSAFE` builds the static PRNG mutex serializes both initialization and output generation. In non-threadsafe builds, callers rely on the global SQLite threading mode contract.

## Risks and Edge Cases
Reset behavior is triggered by `N<=0` or `pBuf==NULL`; callers that accidentally pass a null buffer clear the PRNG state instead of getting an error. Initialization failure from `sqlite3_initialize()` returns without filling the output buffer, leaving caller-provided memory unchanged.

The no-VFS path zero-fills seed material, which would make output deterministic, but it is guarded by `NEVER(pVfs==0)` because normal SQLite initialization should always provide a VFS. VFS randomness quality directly affects PRNG unpredictability.

Counter overflow is not explicitly handled. The 32-bit `s[12]` counter increments once per 64-byte block. Exhausting the counter would require very large output volume from one seed; still, tests or analysis of long-running processes should be aware of the absence of a reseed or multiword counter increment.

The output cache accounting is non-obvious because partial fits copy from the tail of `out`, while draining cached bytes copies from the head. Changes to this logic can silently alter deterministic test expectations and should be tested through save/restore.

## Test Signals
Tests should cover reset followed by deterministic test-control save/restore, requests of 1 byte, 63 bytes, 64 bytes, 65 bytes, and multiple blocks; calls that exactly consume cached bytes; calls that partially consume cached bytes; `N<=0` reset; `pBuf==NULL` reset; auto-initialization failure handling where injectable; and concurrent calls in threadsafe builds.

ChaCha block tests can compare against known RFC 7539 block outputs for a fixed state if exposed through a test harness. VFS integration tests should verify that first use calls the VFS randomness provider and that saved/restored PRNG state reproduces byte streams exactly.
