# File Research: sources/local-fs/ocfs2-tools/libocfs2/feature_string.c

Purpose: parses, merges, orders, and prints OCFS2 feature flags.

Key responsibilities:
- Defines feature-level defaults for `default`, `max-compat`, and `max-features`.
- Defines mkfs type defaults.
- Maps supported feature strings to own flags and dependency-expanded flags.
- Maps all printable superblock, tunefs, extent, refcount, and o2cb cluster flags to names.
- Parses comma-separated feature strings with `no` prefixes for clearing.
- Merges feature level defaults with explicit set and clear requests.
- Orders features forward or reverse by dependency relationships for tunefs-style operations.
- Prints unknown when supplied flags include bits not in the name tables.

Important APIs:
- `ocfs2_parse_feature_level()`
- `ocfs2_snprint_feature_flags()`
- `ocfs2_snprint_tunefs_flags()`
- `ocfs2_snprint_extent_flags()`
- `ocfs2_snprint_refcount_flags()`
- `ocfs2_snprint_cluster_o2cb_flags()`
- `ocfs2_merge_feature_flags_with_level()`
- `ocfs2_parse_feature()`
- `ocfs2_feature_foreach()`, `ocfs2_feature_reverse_foreach()`

Core invariants:
- Enabling a feature can include dependency flags through `ff_flags`.
- Clearing a feature clears dependent features via `ocfs2_feature_clear_deps()`.
- Set and clear masks must not conflict.
- Name tables are expected to stay synchronized with `ocfs2_fs.h`.

Supported feature strings include:
- `local`, `sparse`, `backup-super`, `unwritten`, `extended-slotmap`, `inline-data`, `metaecc`, `xattr`, `indexed-dirs`, `usrquota`, `grpquota`, `refcount`, `discontig-bg`, `clusterinfo`, `append-dio`.

Notable behavior:
- The parser treats any token starting with literal `no` as a clear request and strips those two characters before matching.
- `ocfs2_parse_feature()` uses `strdup()` directly and does not check for allocation failure before tokenizing.
- Dependency ordering uses `qsort()` over feature indices and comparator logic based on feature dependency masks.
