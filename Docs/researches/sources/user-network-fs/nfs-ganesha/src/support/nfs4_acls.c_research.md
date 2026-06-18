# sources/user-network-fs/nfs-ganesha/src/support/nfs4_acls.c

## Purpose
This file manages shared NFSv4 ACL objects. It allocates ACE arrays and ACL containers, interns identical ACL payloads in a hash table, and reference-counts cached ACLs so FSAL objects can share equivalent ACLs without duplicating memory.

## Important APIs, Types, And Functions
Global state includes `pool_t *fsal_acl_pool` and static `hash_table_t *fsal_acl_hash`. Public functions are `nfs4_ace_alloc`, `nfs4_acl_alloc`, `nfs4_ace_free`, `nfs4_acl_free`, `nfs4_acl_entry_inc_ref`, `nfs4_acl_new_entry`, `nfs4_acl_release_entry`, and `nfs4_acls_init`. Internal hashing uses `CityHash64` through `fsal_acl_hash_both`; `compare_fsal_acl` compares raw ACE bytes.

## Control Flow
`nfs4_acls_init` creates the ACL pool and hash table. New ACL data enters through `nfs4_acl_new_entry`, which builds a key over `acldata->aces`, latches the hash table, and either returns an existing ACL after freeing the duplicate ACE array and incrementing the refcount, or creates a new `fsal_acl_t`, owns the ACE array, initializes refcount 1, and inserts it. `nfs4_acl_release_entry` decrements under the ACL lock. If it is the last reference, it latches the hash table, checks the entry again to handle races, deletes the table entry, and frees the ACL and ACE array.

## State And Persistence
All state is process-local. ACL identity is derived from raw ACE array bytes, not from a serialized external key. Persistence is limited to long-lived in-memory pool and hash entries until references are released or the server exits.

## Dependencies And Integration Points
The file depends on Ganesha memory pools, hash table latches, `fsal_types.h`, logging, `city.h`, and `nfs4_acls.h`. It sits between protocol/FSAL ACL conversion code and object metadata, giving FSAL handles a shared `fsal_acl_t` representation.

## Risks And Test Signals
Risks include raw-structure hashing sensitivity to padding or uninitialized ACE fields, refcount races if callers use ACLs after release, missing cleanup for the global hash/pool on shutdown, and asserting `old_value.addr == acl` during final deletion. Test signals should cover interning identical ACLs, distinct ACL byte sequences, release while another thread increments, duplicate insert latch paths, allocation failure paths, and static analysis for padding-sensitive comparisons.
