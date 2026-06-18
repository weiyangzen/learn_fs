<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/048 -->
# sources/test-tools/xfstests/tests/ext4/048

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/048_research.md`.

Source read: 208 lines, SHA256 prefix `42c20d9891305069`.

Purpose: FS QA Test No. 048 Test wiping of ext4_dir_entry2 data upon file removal, conversion to htree, and splitting of htree nodes Import common functions..

Important APIs/types/functions: test tags `auto quick dir`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_od_endian_flag`; helper functions `get_block()`, `get_offset()`, `get_reclen()`, `read_dir_ent()`, `induce_node_split()`; key variables `big_endian=$(echo -ne '\x11' | od -tx2 | head -1 | cut -f2 -d' ' | cut -c1)`, `testdir="${SCRATCH_MNT}/testdir"`, `dir_size="$(stat --printf="%s" $testdir)"`, `file_num=$(($file_num + 1))`, `test_file1="test0001"`, `test_file2="test0002"`, `test_file3="test0003"`, `blocksize="$(_get_block_size $SCRATCH_MNT)"`, `file_num=1`, `block1=$(get_block $test_file1)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `get_block()`, `get_offset()`, `get_reclen()`, `read_dir_ent()`, `induce_node_split()`. Representative operation sequence: L20: _require_command "$DEBUGFS_PROG" debugfs; L67: _scratch_mount >> $seqres.full 2>&1; L78: _scratch_unmount >> $seqres.full 2>&1; L89: _scratch_mkfs_sized $((1 * 1024 * 1024 * 1024)) >> $seqres.full 2>&1; L93: _scratch_mount >> $seqres.full 2>&1; L97: if test -x $here/src/checkpoint_journal && \; L98: ! $here/src/checkpoint_journal $SCRATCH_MNT --dry-run ; then; L108: _scratch_unmount >> $seqres.full 2>&1; L119: _scratch_mount >> $seqres.full 2>&1; L121: _scratch_unmount >> $seqres.full 2>&1; L135: _scratch_mount >> $seqres.full 2>&1; L137: _scratch_unmount >> $seqres.full 2>&1; L154: check_htree=$($DEBUGFS_PROG $SCRATCH_DEV -R "htree_dump /testdir" 2>&1); L163: check_htree=$($DEBUGFS_PROG $SCRATCH_DEV -R "htree_dump /testdir" 2>&1); L182: hdump=$($DEBUGFS_PROG $SCRATCH_DEV -R "htree_dump /testdir" 2>> $seqres.full).

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Test 1 part 1 passed.; Test 3 passed..
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/048 -->
