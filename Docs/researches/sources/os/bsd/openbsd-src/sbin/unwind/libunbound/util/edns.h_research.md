# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.h

## Role

`edns.h` declares EDNS client-string storage and DNS COOKIE secret/hash APIs used by the parser, config, and resolver runtime.

## Data Structures

`struct edns_strings` contains an address-prefix `rbtree_type`, the EDNS client-string option code, and a regional allocator. `struct edns_string_addr` embeds `addr_tree_node` first for tree use and stores the configured string plus length.

`UNBOUND_COOKIE_HISTORY_SIZE` is `2`, and `UNBOUND_COOKIE_SECRET_SIZE` is `16`. `struct cookie_secret` stores one secret, while `struct cookie_secrets` wraps the active/staging secret array with a basic lock and count.

`enum edns_cookie_val_status` reports cookie validation states: client-only, future, expired, invalid, valid, and valid-needs-renewal.

## Public API

The header declares EDNS string creation/deletion, config application, address lookup, memory accounting, and tree swapping.

The DNS COOKIE API includes server-cookie hash generation, cookie writing, single-secret validation, cookie-secret allocation/deletion, config/file loading, multi-secret validation, adding a staging secret, activating a staging secret, and dropping a staging secret.

## Research Notes

The comments document RFC9018 input layout for cookie hashing and writing. Callers of secret mutation functions are expected to hold the lock, while validation functions perform their own locking around the shared secret list.
