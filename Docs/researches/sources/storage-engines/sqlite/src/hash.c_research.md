# sources/storage-engines/sqlite/src/hash.c

## Purpose

`hash.c` implements SQLite's small internal case-insensitive string-key hash table. It is used for schema and function lookup structures where keys are stable strings owned elsewhere. The implementation combines a global doubly linked element list with an optional bucket table that is allocated only after the table grows.

## Important APIs, Types, And Functions

The public internal API is `sqlite3HashInit()`, `sqlite3HashClear()`, `sqlite3HashFind()`, and `sqlite3HashInsert()`, declared in `hash.h`. Internal helpers are `strHash()`, `insertElement()`, `rehash()`, `findElementWithHash()`, and `removeElement()`.

`strHash()` computes a case-insensitive hash with Knuth multiplicative mixing, masking off the ASCII or EBCDIC case bit. Equality is still checked with `sqlite3StrICmp()`. `rehash()` allocates the bucket array with `sqlite3Malloc()` inside benign malloc hooks, caps size with `SQLITE_MALLOC_SOFT_LIMIT`, uses `sqlite3MallocSize()` to account for actual allocation size, and reinserts all elements into buckets. `sqlite3HashInsert()` inserts, replaces, or deletes by passing non-null data, replacement data, or NULL data respectively.

## Control Flow

Initialization zeroes the `Hash` object. Lookups compute the hash and either scan the bucket's chain/count range or linearly scan the global list when no bucket table exists. Insert first searches for an existing key. If found, non-null data replaces the payload and key pointer while NULL data removes the element. If not found and data is non-null, it allocates a `HashElem`, stores the caller-owned key pointer and data pointer, increments count, optionally rehashes when count is at least five and more than twice the bucket count, then links the element into the bucket/list. Deleting the last element calls `sqlite3HashClear()` to release the bucket table and reset the structure.

## State And Persistence Behavior

All state is in-memory in the caller-provided `Hash` object plus heap-allocated `HashElem` and bucket array memory. Keys and payloads are not owned by the hash table; `sqlite3HashClear()` frees elements and buckets but not `pKey` strings or `data` payloads. There is no persistence and no built-in locking.

## Dependencies And Integration Points

The implementation depends on `sqliteInt.h`, SQLite memory APIs, `sqlite3StrICmp()`, benign malloc hooks from `fault.c`, `SQLITE_MALLOC_SOFT_LIMIT`, and the `Hash`/`HashElem` layout in `hash.h`. It is used by schemas (`tblHash`, `idxHash`, `trigHash`, `fkeyHash`) and by global function registration/lookup.

## Risks

Callers must keep key strings alive and must separately manage payload lifetime. An allocation failure during new-element allocation is hard for insertion and returns the input data pointer, while rehash allocation failure is benign and leaves the table valid but potentially slower. The bucket `chain` pointer references the first element in a contiguous run within the global linked list; insertion/removal must preserve bucket counts and list order. Case-insensitive hashing means keys differing only by case replace each other. No thread safety exists without external schema/function mutexes.

## Test Signals

Signals include insertion, replacement, deletion, deleting the last element, lookup before and after rehash, forced rehash OOM preserving all entries, case-insensitive key matching, `sqliteHashFirst()`/`sqliteHashNext()` iteration over all elements, soft-limit builds, and schema/function lookup tests that exercise hash lifetime under schema reset.
