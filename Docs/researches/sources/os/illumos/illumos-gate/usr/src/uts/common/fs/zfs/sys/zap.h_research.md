# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zap.h

This public header declares the ZFS Attribute Processor, a DMU-backed name/value object store used for directories, metadata maps, feature state, and many pool/filesystem tables.

Core model:
- ZAP objects store zero-terminated string names up to `ZAP_MAXNAMELEN` and integer-array values up to `ZAP_MAXVALUELEN`, with element sizes of 1, 2, 4, or 8 bytes.
- `matchtype_t` controls normalized/case-sensitive matching.
- `zap_flags_t` selects 64-bit hashes, uint64-array binary keys, and pre-hashed keys.

Public API surface:
- Create APIs support normal, normalized, flag-controlled, linked, claimed, and custom dnode-size ZAP objects.
- Lookup APIs support strings, normalized string lookup, uint64-array keys, dnode-based lookup, prefetch, containment, and write-count estimation.
- Mutation APIs add, update, length-query, remove, count, value-search, join, join-key, join-increment, int-key helpers, and increment helpers.
- Cursor APIs initialize/finalize, retrieve, advance, serialize, and resume serialized positions.
- `zap_attribute_t` reports integer length, normalization conflicts, count, first integer, and name.
- `zap_stats_t` exposes internal pointer table, block, leaf, entry, salt, and histogram statistics for diagnostic users.

Risk-sensitive invariants:
- ZAP routines are thread-safe at the object level, but a DMU transaction must not be operated on concurrently.
- Integer-size conversion never sign-extends and may return overflow for too-small buffers.
- Serialized cursor cookies are persistent and reserve low bits for type differentiation.
- Normalization conflict handling matters for case-insensitive or Unicode-normalized datasets.
