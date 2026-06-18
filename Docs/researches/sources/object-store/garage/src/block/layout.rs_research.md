# sources/object-store/garage/src/block/layout.rs

Purpose: maps block hashes to local data directories and manages multi-drive layout migration for block files.

Important APIs/types/functions: `DataLayout` with `data_dirs`, marker map, primary partition vector, and secondary partition vectors; `DataDir` and `DataDirState::{Active, ReadOnly}`; `initialize`, `update`, `check_markers`, `primary_block_dir`, `secondary_block_dirs`, `without_secondary_locations`; helpers `make_data_dirs` and `dir_not_empty`.

Control flow: layout initialization splits 1024 hash partitions proportionally over active directory capacity. Existing non-empty directories become secondary locations for partitions they do not primarily own, preventing older data from being lost. `update` preserves old primary assignments where possible, moves excess primaries to secondary, fills unassigned partitions according to new capacities, and detects newly added non-empty directories as secondary sources.

State and persistence: `DataLayout` implements `InitialFormat` with marker `G09bmdl` and is persisted by `BlockManager` under metadata as `data_layout`. Per-directory `garage-marker` files bind persisted layout entries to actual mountpoints and prevent accidental mount/path swaps.

Dependencies and integration points: consumes `garage_util::config::DataDirEnum`, `bytesize` parsing, `hex`, `garage_util::data::Hash`, and migration/error helpers. Used by block manager to decide primary write directory, read fallback directories, rebalance traversal, and post-rebalance cleanup.

Risks: uses assertions for invariants such as nonzero active capacity and exactly 1024 partitions; invalid persisted/config state can panic. `dir_not_empty` treats marker files and hex-named directories as meaningful data, so unusual user files may influence secondary-location behavior. Marker mismatch errors are intentionally strict because wrong mounts can corrupt data placement assumptions.

Test signals: no file-local unit tests; test coverage is mostly operational/integration. Manual validation should cover single-dir, multiple active dirs, read-only dirs, capacity changes, removed dirs, non-empty added dirs, and marker mismatch cases.
