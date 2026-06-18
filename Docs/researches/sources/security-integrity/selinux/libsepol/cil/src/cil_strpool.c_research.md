# sources/security-integrity/selinux/libsepol/cil/src/cil_strpool.c

## Purpose

`cil_strpool.c` implements a process-global intern pool for strings. It deduplicates equal strings and returns stable canonical `char *` pointers so much of CIL can compare keywords and identifiers by pointer identity.

## Important APIs, Types, and Functions

`cil_strpool_init()` lazily creates a hashtab and increments a reader/reference count. `cil_strpool_add(const char *str)` looks up a string under a mutex, inserts a `cil_strdup()` copy if absent, and returns the canonical stored pointer. `cil_strpool_destroy()` decrements the reader count and destroys the pool when it reaches zero. Internal helpers implement djb-style hashing, `strcmp()` comparison, and entry destruction.

## Control Flow

All public operations lock `cil_strpool_mutex`. Add searches first; on miss it allocates `struct cil_strpool_entry`, duplicates the input string, inserts it using the duplicated string as the key, and exits the process on allocation/insert failure. Destroy maps entries to free both string and entry before destroying the hashtab.

## State and Persistence Behavior

The pool is static global state: `cil_strpool_tab` and `cil_strpool_readers` persist across CIL database instances. Canonical strings remain valid until the final matching destroy call. The reference count allows multiple users to share the pool, but the code assumes balanced init/destroy calls.

## Dependencies and Integration Points

The implementation uses pthread mutexes, libsepol `hashtab_t`, CIL memory helpers, and CIL logging. It underpins keyword and identifier identity comparisons throughout parser, resolver, verifier, and tree logging code.

## Risks and Test Signals

Unbalanced destroy can underflow `cil_strpool_readers` because it is unsigned and not guarded. Calling `cil_strpool_add()` before init would search a null hashtab. The table size is a power of two and the hash masks by `h->size - 1`, so changing size must preserve that assumption. Tests should cover duplicate string interning, concurrent adds of the same string, balanced multi-reader init/destroy, and misuse detection if the broader project has debug assertions.
