<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/342 -->
# sources/test-tools/xfstests/tests/btrfs/342

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/342_research.md`.

Source read: 103 lines, SHA256 prefix `2b8b8103cd2bd655`.

Purpose: FS QA Test No. 342 Test free space tree mount options, for newer kernels with only 2 options involed: - No space cache - New (default) v2 space cache.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_fs_feature free_space_tree`, `_require_btrfs_no_block_group_tree`; helper functions `mkfs_nocache()`, `mkfs_v2()`, `check_fst_compat()`; key variables `compat_ro="$($BTRFS_UTIL_PROG inspect-internal dump-super "$SCRATCH_DEV" | \`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `mkfs_nocache()`, `mkfs_v2()`, `check_fst_compat()`. Representative operation sequence: L15: _require_btrfs_command inspect-internal dump-super; L16: _require_btrfs_fs_feature free_space_tree; L20: _require_btrfs_no_block_group_tree; L24: _scratch_mkfs >/dev/null 2>&1; L25: _scratch_mount -o clear_cache,nospace_cache; L26: _scratch_unmount; L31: _scratch_mkfs >/dev/null 2>&1; L32: _scratch_mount -o space_cache=v2; L33: _scratch_unmount; L38: compat_ro="$($BTRFS_UTIL_PROG inspect-internal dump-super "$SCRATCH_DEV" | \; L58: _scratch_mount -o nospace_cache; L60: _scratch_unmount; L64: _scratch_mount -o space_cache=v2; L66: _scratch_unmount; L76: _try_scratch_mount -o nospace_cache >/dev/null 2>&1 || echo "mount failed"; L80: _scratch_mount; L82: _scratch_unmount; L83: _scratch_mount -o space_cache=v2.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include free space tree is enabled; free space tree is disabled; Using no space cache; Enabling free space tree; Trying to mount without free space tree; Mounting existing free space tree.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/342 -->
