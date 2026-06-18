<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/026 -->
# sources/test-tools/xfstests/tests/ext4/026

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/026_research.md`.

Source read: 108 lines, SHA256 prefix `2425678ae6864fa0`.

Purpose: FS QA Test 026 Test for ea_inode feature in ext4. Without ea_inode feature, an extended attribute in ext4 cannot be larger than the fs block size. ea_inode feature allows storing xattr values in external inodes and so raises xattr value size limit to 64k. Import common functions..

Important APIs/types/functions: test tags `auto quick attr`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`, `_require_scratch_ext4_feature "ea_inode"`; helper functions `attr_set()`, `attr_list()`, `attr_remove()`; key variables `tmp=$(_getfattr --absolute-names --only-values -n $name $file)`, `y=$SCRATCH_MNT/y`, `z=$SCRATCH_MNT/z`, `name_in_ibody=user.i`, `name_in_block=user.$(perl -e 'print "b" x 100;')`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `attr_set()`, `attr_list()`, `attr_remove()`. Representative operation sequence: L24: _require_scratch_ext4_feature "ea_inode"; L26: _scratch_mkfs_ext4 -O ea_inode >/dev/null 2>&1; L27: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/026 -->
