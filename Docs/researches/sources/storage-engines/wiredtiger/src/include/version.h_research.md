<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/version.h -->
# Research: sources/storage-engines/wiredtiger/src/include/version.h

## Purpose

`version.h` defines WiredTiger's compact internal version value and inline comparison helpers. The same representation is used for general WiredTiger release/compatibility versions and, through `WT_BTREE_VERSION`, for btree source-file version ranges.

The header gives callers a consistent way to represent absent versions, partially specified major/minor versions, and full major/minor/patch versions without repeating comparison logic.

## Important APIs, Types, and Functions

`struct __wt_version` contains `uint16_t major`, `uint16_t minor`, and `uint16_t patch`. `wt_internal.h` typedefs this as `WT_VERSION`.

`typedef WT_VERSION WT_BTREE_VERSION` aliases the same structure for btree version numbers, avoiding confusion at call sites that compare file format ranges instead of WiredTiger release versions.

`WT_NO_VALUE` is `UINT16_MAX`. `WT_NO_VERSION` is a compound literal with all three fields set to `WT_NO_VALUE`.

`__wt_version_cmp(WT_VERSION v, WT_VERSION other)` returns `1`, `0`, or `-1` like `strcmp`. If either input has `patch == WT_NO_VALUE`, the function sets both local patch fields to `0`, making patch optional for comparisons. Major and minor are compared first, then patch if both patches are defined.

`__wt_version_defined(WT_VERSION v)` returns true when major and minor are not `WT_NO_VALUE`. Patch is intentionally not required.

`__wt_version_eq`, `__wt_version_gt`, `__wt_version_gte`, `__wt_version_lt`, and `__wt_version_lte` are small inline wrappers over `__wt_version_cmp`.

## Control Flow

All functions are `static WT_INLINE` and operate on pass-by-value structures, so they have no side effects. Comparison first normalizes missing patch values locally, checks full equality, then performs ordered major/minor/patch greater-than checks. If no greater-than branch matches and equality was false, the result is less-than.

The wrapper predicates do not duplicate ordering logic. They interpret the tri-state comparison result, which keeps optional-patch behavior consistent across equality and range checks.

## State and Persistence Behavior

This header does not maintain state. It defines value semantics for version fields stored elsewhere.

Connection compatibility code initializes `max_compat`, `min_compat`, and `new_compat` to `WT_NO_VERSION`, parses configuration into major/minor fields, stores the current compatibility in `conn->compat_version`, and persists/reloads compatibility through metadata/turtle paths. `conn->recovery_version` is also initialized to `WT_NO_VERSION` during open before turtle validation populates it.

Metadata and checkpoint code use the same value semantics when reading persisted version strings. `meta_turtle.c` reads `major`, `minor`, and `patch` from the turtle file, compares the result with `WT_MIN_STARTUP_VERSION`, and stores it as the recovery version. `meta_ckpt.c` reads btree major/minor versions from checkpoint metadata and checks them against `WT_BTREE_VERSION_MIN` and `WT_BTREE_VERSION_MAX`.

## Dependencies and Integration Points

The header depends on fixed-width integer types, `bool`, `UINT16_MAX`, and `WT_INLINE` being available from the surrounding WiredTiger include stack.

It integrates with connection configuration in `conn/conn_reconfig.c`, where `__wti_conn_compat_config` uses `__wt_version_defined`, `__wt_version_eq`, `__wt_version_lt`, and `__wt_version_gt` to enforce compatibility release, required minimum, and required maximum constraints.

It integrates with startup validation in `conn/conn_api.c` and `meta/meta_turtle.c`, where saved turtle versions are validated before modifying an existing database home.

It integrates with btree/checkpoint metadata via `WT_BTREE_VERSION` and the min/max btree version constants used by checkpoint validation.

## Risks and Edge Cases

`WT_NO_VALUE` is a sentinel inside a `uint16_t` field. Versions cannot use `65535` as a meaningful major, minor, or patch value without colliding with the undefined marker.

Missing patch values are ignored symmetrically. Comparing `1.2.NO_VALUE` to `1.2.9` returns equal because both patch fields are normalized to zero when either patch is missing. This is deliberate for callers that only know major/minor, but it can surprise code that expects a missing patch to be lower or higher than a concrete patch.

`__wt_version_defined` only checks major and minor. A value with major/minor set and patch omitted is a valid defined version, while a value with only patch set is undefined even if `patch != WT_NO_VALUE`.

The comparison helpers do not validate ranges beyond the sentinel rule. Parsing code must still reject invalid textual formats and ensure values fit in `uint16_t`.

Because `WT_NO_VERSION` is a compound literal macro, it is convenient for assignment and initialization in C code but should not be treated as a stable object address.

## Test Signals

Unit or compile-level tests should cover comparison matrices around major, minor, and patch ordering; equality when either patch is `WT_NO_VALUE`; and `__wt_version_defined` for full, major/minor-only, and sentinel values.

Integration tests should exercise compatibility configuration on open and reconfigure, especially `require_min`, `require_max`, unchanged compatibility reconfiguration, and saved metadata compatibility checks. Startup/recovery tests should cover turtle versions below `WT_MIN_STARTUP_VERSION` and btree checkpoint versions outside the supported min/max range.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/version.h -->
