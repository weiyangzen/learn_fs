# sources/storage-engines/sqlite/src/bitvec.c

## Purpose

`bitvec.c` implements SQLite's fixed-size sparse-or-dense bitmap abstraction for page-number sets. It is used by pager and transaction code to remember pages that have been journaled or marked with properties such as "dont-write". Bits are numbered from 1, while the implementation normalizes internally to zero-based offsets.

## Important APIs, Types, And Functions

The public internal API consists of `sqlite3BitvecCreate()`, `sqlite3BitvecTest()`, `sqlite3BitvecTestNotNull()`, `sqlite3BitvecSet()`, `sqlite3BitvecClear()`, `sqlite3BitvecDestroy()`, and `sqlite3BitvecSize()`. Debug builds also expose `sqlite3ShowBitvec()`, and testable builds include `sqlite3BitvecBuiltinTest()`.

`struct Bitvec` is exactly `BITVEC_SZ` bytes, normally 512. It stores `iSize`, `nSet`, `iDivisor`, and a union with three representations: `aBitmap` for small dense vectors up to `BITVEC_NBIT`, `aHash` for sparse large vectors up to `BITVEC_MXHASH` entries, and `apSub` for recursive sub-bitmaps once the hash fills.

## Control Flow

Creation zeroes one fixed-size object and records its maximum bit. Test operations return false for NULL or out-of-range inputs, then descend through recursive sub-bitmaps when `iDivisor` is nonzero. Leaf tests either inspect a byte bitmap or probe the open-addressed hash table.

Set operations accept NULL as success, require valid one-based indexes by assertion, descend or allocate sub-bitmaps as needed, set a direct bitmap bit for small leaves, or insert the one-based value into the hash table. If hash occupancy reaches `BITVEC_MXHASH`, the node converts to recursive form: it stack-copies the old hash table, clears the union as sub-pointers, computes `iDivisor`, inserts the new bit, reinserts all old bits, and frees the stack allocation.

Clear operations are optimized for rarity. They descend to a leaf, clear direct bitmap bits in place, or rebuild the hash table from a caller-supplied temporary `BITVEC_SZ` buffer while omitting the cleared value. Destruction recursively frees sub-bitmaps and then the current node.

## State And Persistence Behavior

Bitvec state is in-memory only and is owned by callers. It records membership but not ordering. `nSet` is valid only for hash leaves. Recursive nodes divide the original bit range into fixed-size bins; sub-bitmaps are lazily allocated. Because clear requires external scratch storage, callers must provide a buffer large enough to hold the hash snapshot. No state is written directly to disk, but incorrect membership can affect pager journaling decisions and therefore durability.

## Dependencies And Integration Points

The file depends on SQLite allocation helpers (`sqlite3MallocZero`, `sqlite3_free`, `sqlite3StackAllocRaw`, `sqlite3StackFree`), integer typedefs, randomness and malloc for the built-in test, and debug printing. Pager users rely on the abstraction to efficiently handle common sparse sets and rare dense sets without allocating memory proportional to the database page count.

## Risks And Edge Cases

Key risks are one-based versus zero-based indexing, maximum `u32` sizes, hash-table wraparound, preserving values during hash-to-recursive conversion, and the unusual clear API that requires temporary storage from the caller. `sqlite3BitvecSet()` ORs reinsertion return codes during rehash, so OOM must be propagated without corrupting enough state to break cleanup. Very large databases exercise recursive `iDivisor` math and pending dense cases such as dropping a large table.

## Test Signals

`sqlite3BitvecBuiltinTest()` is the primary local signal. It compares the Bitvec against a linear byte-array reference across scripted set, clear, random set, random clear, induced mismatch, debug print, and compile-parameter operations. Additional pager-level tests should stress journaled-page tracking for small databases, sparse large databases, dense page sets, OOM during sub-bitmap allocation, and clears after rehash.
