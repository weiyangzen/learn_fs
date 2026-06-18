# sources/user-network-fs/nfs-ganesha/src/support/nfs_ip_name.c

## Purpose
This file implements the IP-address-to-hostname cache used by dispatch/export code for logging, client identity display, and auth statistics. It resolves socket addresses with `getnameinfo`, caches hostnames keyed by `sockaddr_t`, and expires entries after a configurable interval.

## Important APIs, Types, And Functions
Global state is `hash_table_t *ht_ip_name` and `unsigned int expiration_time`. Public functions are `ip_name_value_hash_func`, `ip_name_rbt_hash_func`, `compare_ip_name`, `display_ip_name_key`, `display_ip_name_val`, `nfs_ip_name_add`, `nfs_ip_name_get`, `nfs_ip_name_remove`, and `nfs_Init_ip_name`. The configuration block `nfs_ip_name` exposes `NFS_IP_Name` parameters `Index_Size` and `Expiration_Time`.

## Control Flow
`nfs_ip_name_add` performs DNS lookup into the caller's buffer, falls back to numeric IP text on failure, logs slow lookups, allocates a copied sockaddr key and variable-length hostname value, and inserts into the hash table while tolerating duplicate-key races. `nfs_ip_name_get` looks up the address, evicts expired values, copies the hostname to the caller, and reports miss or success. `nfs_ip_name_remove` deletes a cached entry and frees its value. `nfs_Init_ip_name` initializes the hash table from parsed config.

## State And Persistence
Cache entries are process-local heap allocations with timestamps. They are not persisted. Key memory is allocated on insert, but only value memory is explicitly freed on delete in this file; key cleanup likely depends on hash-table ownership semantics.

## Dependencies And Integration Points
The code depends on Ganesha hash tables, socket hashing/comparison/display helpers, allocation helpers, config parsing, logging, and `gsh_getnameinfo`. It integrates with core config through the exported `config_block` and with dispatch paths needing reverse DNS or address display.

## Risks And Test Signals
Risks include slow or blocking DNS during cache miss, fallback requiring caller buffers at least `SOCK_NAME_MAX`, stale names until expiry, prime-size validation only at config commit, and duplicate insert races that intentionally discard the losing allocation. Tests should cover DNS success/failure, numeric fallback, too-small caller buffers, expiry eviction, duplicate insert, remove miss/hit, IPv4 and IPv6 keys, and non-prime config rejection.
