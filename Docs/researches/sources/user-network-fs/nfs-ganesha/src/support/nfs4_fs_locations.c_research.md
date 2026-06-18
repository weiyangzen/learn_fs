# sources/user-network-fs/nfs-ganesha/src/support/nfs4_fs_locations.c

## Purpose
This file implements allocation, reference counting, and release for `fsal_fs_locations_t`, the NFSv4 fs_locations data structure used to describe alternate filesystem roots and server locations.

## Important APIs, Types, And Functions
Public functions are `nfs4_fs_locations_new`, `nfs4_fs_locations_free`, `nfs4_fs_locations_get_ref`, and `nfs4_fs_locations_release`. Internal `nfs4_fs_locations_alloc` allocates the structure and optional server array, while `nfs4_fs_locations_put_ref` decrements a reference with the caller holding the write lock.

## Control Flow
`nfs4_fs_locations_new` allocates a zeroed structure, duplicates `fs_root` and `rootpath`, initializes refcount 1, and returns it. Callers increment with `nfs4_fs_locations_get_ref`. Release takes the write lock; if the refcount is greater than one it decrements and returns, otherwise it drops the lock and frees all owned strings, server string values, the server array, the lock, and the object.

## State And Persistence
Each object owns duplicated root strings, an optional `utf8string` server array, a lock, and a reference count. There is no global cache or durable persistence. Lifetime is entirely caller-managed through the reference API.

## Dependencies And Integration Points
The code uses `nfs4_fs_locations.h`, `fsal_types.h`, Ganesha allocation helpers, pthread rwlocks, and NFSv4 logging. It integrates with FSAL and protocol paths that return `fs_locations`/referral style attributes.

## Risks And Test Signals
Risks include no allocation-failure cleanup after `fs_root` or `rootpath` duplication fails, no null check after `server` allocation when `count` is nonzero, and potential races if callers access fields without holding their own reference. Tests should cover zero and nonzero server counts, multiple get/release sequences, release of NULL, allocation failure injection, and server string cleanup.
