# sources/user-network-fs/nfs-ganesha/src/SAL/9p_owner.c

Purpose: manages the 9P lock-owner hash table used by the state abstraction layer to identify lock owners by 9P client address and process id.

Important APIs and types: `Init_9p_hash()`, `get_9p_owner()`, `display_9p_owner()`, `display_9p_owner_key_val()`, `compare_9p_owner()`, `_9p_owner_value_hash_func()`, `_9p_owner_rbt_hash_func()`, `ht_9p_owner`, `state_owner_t`, and `STATE_LOCK_OWNER_9P`.

Control flow: initialization creates `ht_9p_owner` with display, compare, and hash callbacks. Lookup builds a stack `state_owner_t` key with type, refcount, proc id, and copied client address, then delegates to generic `get_state_owner(CARE_ALWAYS, ...)`. Display formats type, pointer, address, proc id, and refcount. Compare checks nulls, pointer identity, and process id; address comparison is compiled out. Hashing adds proc id to IPv4 `sin_addr.s_addr` and uses that for bucket and rb-tree hash.

State and persistence: in-memory hash table only. Owner lifetime and refcounting are managed by generic SAL owner code.

Dependencies and integration points: depends on SAL state-owner infrastructure, Ganesha hash table, logging, display helpers, and 9P feature-gated build inclusion through SAL CMake.

Risks: address comparison is disabled, so owners with the same process id can compare equal even from different clients despite hashing including address. Hashing assumes IPv4 layout and has TODOs noting IPv6 limitations. The stack key sets refcount to 1 for lookup, but actual lifetime is owned by generic owner logic.

Test signals: initialize table, look up same proc/client twice and verify sharing/refcount behavior, look up same proc from different clients to expose compare semantics, IPv6 client address behavior, display output, and hash distribution under many proc ids.
