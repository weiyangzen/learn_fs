# sources/user-network-fs/nfs-ganesha/src/SAL/nlm_state.c

Purpose: Manages the NLM state cache for lock and share state records, mapping an NLM owner/export/object/type tuple to a reusable FSAL `state_t`.

Important APIs, types, and functions: The global `ht_nlm_states` stores NLM `state_t` entries. Entry points are `Init_nlm_state_hash`, `get_nlm_state`, and `dec_nlm_state_ref`, with compare/hash/display helpers `compare_nlm_state`, `nlm_state_value_hash_func`, and `nlm_state_rbt_hash_func`.

Control flow: `get_nlm_state` builds a key from requested state type, owner, current export, NSM state sequence, and object. It latches the hash table, returns an existing state with an atomic ref if possible, or for `CARE_MONITOR` deletes an old state whose `state_seqid` no longer matches the monitor state before creating a replacement. `CARE_NOT` and `CARE_OWNER` do not create new state. Creation allocates FSAL state, initializes state mutex and lock list, takes an active object ref, inserts under the existing latch, takes an export ref, and returns the state. `dec_nlm_state_ref` removes the state from the hash at refcount zero, releases the export, closes FSAL state against the object if still live, destroys the mutex, frees state memory, and drops object refs.

State and persistence behavior: NLM state is in-memory only and keyed by owner/object/export/type. Lock state initializes `state_data.lock.state_locklist`; share state is distinguished in hashing by complementing the hash value. There is no direct recovery persistence in this file; NSM/NLM notification and recovery drive state removal elsewhere.

Dependencies and integration points: Depends on FSAL `alloc_state`, `close2`, and object refs, export refs, NLM owners from `nlm_owner.c`, CityHash, hash latches, LTTng state tracepoints, and `op_ctx` export/FSAL context. NLM lock/share operations call this to bind protocol owners to FSAL state.

Risks: Hashing depends on `state_owner` and `state_obj` being adjacent fields in `state_t`, as stated in comments; struct layout changes could silently break hashing. `CARE_MONITOR` intentionally discards stale monitor-state entries, which is necessary after client reboot but can race with active references. Refcount-zero deletion must close FSAL state before freeing; object reference handling uses both a temporary ref and an active ref. Display output is minimal, reducing diagnostic value during hash collisions or leaks.

Test signals: Cover creating versus finding existing lock/share state, `CARE_NOT`/`CARE_OWNER` no-create behavior, monitor-state mismatch replacement, refcount deletion races, FSAL close invocation, object/export ref balancing, and hash/compare distinction between NLM lock and share state.
