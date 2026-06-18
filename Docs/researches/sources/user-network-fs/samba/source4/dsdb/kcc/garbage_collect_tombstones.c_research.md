# sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.c

## Purpose

`garbage_collect_tombstones.c` implements DSDB garbage collection for deleted objects and expired tombstoned linked-attribute values. It is used by the KCC timed event and by `samba-tool domain expunge tombstones`.

## Important APIs, Types, and Functions

- `dsdb_garbage_collect_tombstones()` is the public entry point. It computes the expunge cutoff from current time and `tombstoneLifetime`, builds a search filter covering deleted objects and expired forward links, assembles needed attributes from the schema, and processes each naming context partition.
- `garbage_collect_tombstones_part()` processes one partition. It finds the Deleted Objects container, searches for candidates with internal/recycled visibility, deletes expired deleted objects, and removes expired deleted forward-link values.

## Control Flow

The public function gets the schema and computes `expunge_time` as `current_time - tombstoneLifetime * 24h`, both as LDAP generalized time and NTTIME. It builds an OR filter containing a custom `DSDB_MATCH_FOR_EXPUNGE` clause for every forward linked attribute, plus an `isDeleted=TRUE`/`whenChanged<=cutoff` clause. It also builds an attribute list containing all forward linked attributes plus `isDeleted`.

For each partition, the helper first tries to find its Deleted Objects DN. If a partition has none, it returns success. It searches the whole partition subtree with flags `DSDB_SEARCH_SHOW_RECYCLED`, `DSDB_SEARCH_SHOW_DN_IN_STORAGE_FORMAT`, and `DSDB_SEARCH_REVEAL_INTERNALS`. For each result with `isDeleted=TRUE`, it skips the Deleted Objects container itself and calls `dsdb_delete()` with recycled visibility and relaxed modify flags. For non-deleted results, it scans attributes, skips non-forward links and back links, parses deleted extended DN values, reads `RMD_CHANGETIME`, compares against cutoff, extracts target GUID, constructs a delete value in `<GUID=...>;DN` form, and batches deletes per object. The batch modify uses `DSDB_REPLMD_VANISH_LINKS`.

## State and Persistence Behavior

This code permanently deletes expired tombstone objects and removes expired link tombstones from forward linked attributes. It reports counts through `num_objects_removed` and `num_links_removed` and may set `error_string` for search failures. It does not wrap the entire run in one transaction; each delete/modify is attempted independently, with warnings for per-object failures.

## Dependencies and Integration Points

It depends on DSDB schema metadata, extended DN parsing, matching rules, recycled-object search flags, repl metadata vanish-link semantics, GUID parsing, and Samba time conversion. It is integrated into KCC periodic maintenance and administrative tombstone expunge tooling.

## Risks

The filter is deliberately complex to avoid loading the entire database unnecessarily. Schema mistakes or match-rule bugs can either miss expired values or return too many objects. The link cleanup path depends on internal extended DN components (`RMD_CHANGETIME`, `GUID`) being present and valid. `tombstoneLifetime` multiplication and subtraction assume sensible values; very large values or current times before the lifetime window could produce unexpected cutoffs. Because individual delete failures are logged but not fatal, partial cleanup is possible.

## Test Signals

Tests should cover partitions without Deleted Objects containers, expired and non-expired deleted objects, skipping the Deleted Objects container, forward-link tombstones before/after cutoff, malformed extended DN values, missing `RMD_CHANGETIME`, invalid GUID components, back-link exclusion, counter increments, search failure error strings, and partial delete/modify failures.
