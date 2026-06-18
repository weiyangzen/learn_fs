# sources/user-network-fs/samba/source3/profile/profile_read.c

## Purpose

`profile_read.c` contains layout-aware helpers for accumulating, validating, and reading smbd profile statistics from TDB records. It is shared by the profiling writer and tools that collect profile data.

## Important APIs, Types, and Functions

- `smbprofile_stats_accumulate()` adds every generated stats field from one `profile_stats` into another using the `SMBPROFILE_STATS_ALL_SECTIONS` macro expansion.
- `smbprofile_magic()` hashes the struct contents and generated field names to produce a layout magic value.
- `smbprofile_collect_tdb()` traverses profile TDB records, accumulates records with matching magic, and returns the number of non-summary workers.
- `smbprofile_persvc_collect_tdb()` traverses per-service records and invokes a user callback.

## Control Flow

Accumulation is generated from macros in `smbprofile.h`, ensuring every counter/time/bytes/iobytes section is handled consistently. Magic computation temporarily enables GnuTLS FIPS lax mode, hashes the zero/current stats bytes plus section/field name strings, derives a little-endian 64-bit value from the SHA1 digest, and restores strict mode.

Collection initializes the destination stats with the expected magic, traverses the TDB read-only, filters values that are not exactly `sizeof(struct profile_stats)` or whose magic differs, counts non-summary worker records, and accumulates accepted stats. Per-service collection similarly filters by minimum key size and value size, then calls the provided callback and stops traversal on callback error.

## State and Persistence

This file does not own persistent state. It interprets records already stored in a TDB by `profile.c`. The magic value is the compatibility guard for persisted binary records.

## Dependencies and Integration Points

Dependencies include TDB traversal APIs, GnuTLS hash functions, Samba byte-order helpers, and generated profile macros. `profile.c` calls `smbprofile_magic()`, `smbprofile_stats_accumulate()`, and collection wrappers; external profile tools can use the TDB collection functions.

## Risks and Edge Cases

- Binary `profile_stats` records are ABI-sensitive; magic filtering prevents mixing incompatible layouts but does not migrate old records.
- FIPS mode is deliberately relaxed for SHA1-based compatibility hashing and must be restored.
- Per-service collection does not check magic, only value size, so callback consumers should validate what they need.

## Test Signals

Tests should validate field accumulation across all macro-generated sections, stable nonzero magic for a layout, rejection of wrong-size and wrong-magic records, worker count excluding summary records, callback error propagation, and FIPS mode restoration around hash computation.
