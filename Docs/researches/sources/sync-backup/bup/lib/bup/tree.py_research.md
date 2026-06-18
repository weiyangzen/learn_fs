## sources/sync-backup/bup/lib/bup/tree.py

Purpose: constructs Git tree objects and `.bupm` metadata blobs from ordered filesystem/archive entries, including optional split-tree layout for very large directories.

Important APIs and control flow: `TreeItem`, `RawTreeItem`, and `SplitTreeItem` model tree entries. `_dir_metadata()` decides whether a `.bupm` is necessary and handles lost metadata during repair. `Stack` is the main builder: callers `push()` directories, `append_to_current()` entries, and `pop()` to write trees. `_write_tree()` writes a normal tree plus optional `.bupm`; `_write_split_tree()` chunks directory entries by name using `RecordHashSplitter`, builds `.bupd` subtrees, abbreviates internal names, and recursively writes upper levels.

State and persistence: stack state is in memory; persistence happens through repo `write_tree` and `write_bupm`. It depends on hashsplit config, Git mode constants, name mangling, `Metadata`, `LostMetadata`, and `add_error()` for duplicate names.

Risks and tests: correctness depends on stable sorting, name abbreviation uniqueness, metadata order matching VFS readers, and split-tree internal names ending in depth markers. Duplicate names are ignored with errors. Strong test signals include `test-get-rewrite-missing` for split-tree repair, `test-gc-removes-incomplete-trees` for incomplete split objects, and tree-splitting tests outside this subset.
