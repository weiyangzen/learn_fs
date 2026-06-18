# sources/sync-backup/bup/test/int/test_vfs.py

Purpose: broad integration coverage for bup virtual filesystem behavior: default modes, cache eviction, metadata augmentation, symlink/blob size and readlink handling, file copy semantics, streaming/seeking reads, tree contents with metadata/Git ordering mismatches, duplicate save-date naming, and split-tree depth parsing.

Important APIs/types/functions: `vfs.default_*_mode`, `vfs._cache`, `vfs.cache_notice`, `vfs.clear_cache`, `vfs.resolve`, `vfs.contents`, `vfs.item_size`, `vfs.readlink`, `vfs.augment_item_meta`, `vfs.copy_item`, `vfs.fopen`, `vfs._reverse_suffix_duplicates`, `vfs._parse_tree_depth`, `LocalRepo`, `Metadata`, `write_random`, `tree_dict`, and bup CLI `init/index/save`.

Control flow: cache tests reduce max items and verify eviction. `run_augment_item_meta_tests()` resolves saved file/link items, manually thaws metadata, removes size or replaces metadata with modes, and checks augmentation behavior with and without `include_size`. `test_misc()` creates and saves a file plus symlink, inspects Git tree rows, checks readlink/item_size, resolves latest, and verifies copy independence. Read tests generate random file sizes up to 2 MiB, save them, then compare VFS streaming and seek reads against original files for random block sizes. Ordering tests create `foo` directory and `foo.` file to compare VFS contents with independently parsed trees. Duplicate-date tests save the same timestamp 11 times and assert suffix names. Tree-depth parsing accepts valid `..N.bupd` names and rejects malformed ones.

State and persistence behavior: mutates global VFS cache settings, environment variables (`GIT_DIR`, `BUP_DIR`, `TZ`), `git.repodir`, temporary repositories, Git objects, symlinks, random file contents, and timezone state. Cache cleanup in `finally` prevents cross-test contamination.

Dependencies/integration points: integrates CLI saves, Git object inspection, VFS readers, metadata records, split-tree support, random content generation from `_helpers`, and independent `buptest.vfs` tree parsing.

Risks and test signals: read tests are randomized but print seeds for reproduction. Tests assume symlink support and functioning bup CLI. Signals include exact cache dictionaries, item metadata values, byte-for-byte read comparisons, independent tree-content equality, duplicate suffix ordering, and expected parse exceptions.
