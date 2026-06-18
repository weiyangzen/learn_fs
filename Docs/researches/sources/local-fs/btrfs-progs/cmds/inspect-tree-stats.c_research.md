# File Research: sources/local-fs/btrfs-progs/cmds/inspect-tree-stats.c

## Purpose
Implements `btrfs inspect-internal tree-stats`, which computes size, layout, seek, clustering, inline data, fanout, and read-time statistics for selected Btrfs trees.

## Data Structures
- `struct root_stats` accumulates total nodes/bytes, inline bytes, seek counts and lengths, cluster counts/sizes, bytenr spread, per-level node counts, and an rb-tree histogram of seek distances.
- `struct seek` stores one seek distance bucket and count.

## Traversal
- `calc_root_size()` reads a root by key, initializes stats from the root node, times traversal, prints stats, and frees the seek histogram.
- `walk_nodes()` recursively reads child blocks, counts nodes per level, tracks physical distance between adjacent child blocks, classifies forward/backward seeks, and groups contiguous node clusters.
- `walk_leaf()` counts leaf nodes/bytes and optionally sums inline file-extent payload sizes.

## Output
Prints raw or human-readable totals for tree size, inline data, seeks, average/max seek length, optional histogram, clusters, disk spread, read time, levels, node counts, and average fanout per non-leaf level.

## CLI Behavior
Supports unit options, `-b` for raw bytes, `-t TREEID` for one tree, and `-v` which increments a file-local verbosity counter but is not otherwise used. Without `-t`, it reports root, extent, checksum, and fs trees.

## Safety Note
Warns when the target is mounted because this command accesses block devices directly and can produce inaccurate results or errors if the filesystem changes during traversal.
