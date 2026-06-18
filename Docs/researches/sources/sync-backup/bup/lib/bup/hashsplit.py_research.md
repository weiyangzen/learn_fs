<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hashsplit.py -->
# sources/sync-backup/bup/lib/bup/hashsplit.py

## Purpose
This module wraps the C-backed rolling hash splitter and turns byte streams into Git blobs or hierarchical Git trees. It centralizes bup's content-defined chunking defaults and the repository configuration that affects split compatibility.

## Important APIs, Types, And Functions
Constants include `BUP_BLOBBITS`, `BUP_TREE_BLOBBITS`, `MAX_PER_TREE`, `fanout`, and Git mode constants. `HashSplitter` is imported from `_helpers`. Public helpers are `splitter()`, `configuration()`, `from_config()`, `split_to_blobs()`, `split_to_shalist()`, and `split_to_blob_or_tree()`.

## Control Flow
`configuration(config_get)` reads `bup.split.trees` and optional `bup.split.files`, validating only `legacy:13` through `legacy:21`. `from_config()` filters that map to splitter kwargs. `split_to_blobs()` iterates `(blob, level)` from `HashSplitter`, writes each blob through `makeblob`, and tracks `total_split`. `split_to_shalist()` uses level-triggered `_squish()` to roll lower-level blob entries into intermediate trees, and `split_to_blob_or_tree()` returns either a single blob mode/id or a tree mode/id.

## State And Persistence Behavior
The only module state is configuration defaults and `total_split`. Persistence is indirect: caller-provided `makeblob` and `maketree` write Git objects, usually through `RepoProtocol`/`PackWriter`. The generated tree names are hex offsets padded to total size width.

## Dependencies And Integration Points
It depends on `_helpers.HashSplitter`, `ConfigError`, and `helpers.dict_subset`. It integrates with `cmd/save.py` for file storage, `cmd/get.py` for rewrite compatibility checks, and `git.py`/repo writers for actual object persistence.

## Risks And Edge Cases
`fanout` is mutable global test/config state; invalid or zero values can break assumptions even though an unreachable branch checks zero. Split compatibility depends on exact `blobbits` and tree behavior, so config drift can make rewrite necessary. `_make_shalist()` loads its input list and computes total size, so very large tree levels need memory proportional to entries at that level.

## Test Signals
`test/int/test_hashsplit.py`, `test/int/test_treesplit.py`, `test/ext/test-split-files-config`, `test/ext/test_split_trees.py`, `test/ext/test-treesplit`, and comparative split/join tests validate chunk boundaries, fanout, short reads, file configuration, and tree reconstruction.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/hashsplit.py -->
