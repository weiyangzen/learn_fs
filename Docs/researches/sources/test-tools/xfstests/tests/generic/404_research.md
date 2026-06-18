# sources/test-tools/xfstests/tests/generic/404

## Purpose
Regression test which targets two nasty ext4 bugs in a logic which shifts extents: 1) 14d981f468a1 ("ext4: Include forgotten start block on fallocate insert range") An incorrect right shift (insert range) for the first extent in a range. Test tries to insert many blocks at the same offset to reproduce the following layout: block #0 block #1 |ext0 ext1|ext2 ext3 ...| ^ insert of a new block Because of an incorrect range first block is never reached, thus ext1 is untouched, resulting to a hole at a wrong offset: What we got: block #0 block #1 |ext0 ext1| ext2 ext3 ...| ^ hole at a wrong offset What we expect: block #0 block #1 |ext0 ext1|ext2 ext3 ...| ^ hole at a correct offset 2) 2b3864b32403 ("ext4: do not polute the extents cache while shifting extents") Extents status tree is filled in with outdated offsets while doing extents shift, that leads to wrong data blocks. That is why test writes unique block content and checks md5sum of a result file after each block insert. It is registered as generic/404 with `_begin_fstest` tags `auto, quick, insert, prealloc`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$TEST_DIR/$seq.file, pattern=$tmp.pattern, blksize=`_get_file_block_size $TEST_DIR`. Topic focus: preallocation/range operations, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "falloc"; _require_xfs_io_command "finsert".

External/helper commands: $XFS_IO_PROG, awk, md5sum, rm.

Representative `xfs_io` operations: falloc 0 $(($blksize * 2)); pwrite -i $pattern        0 $blksize; pwrite -i $pattern $blksize $blksize; finsert $blksize $blksize.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: #3 d5562922bd01c2def22f4225aaacd1c2  -; #4 e5f7593f700782765f56f83bd355079b  -; #5 837132f2781fe2153853fba18f5767a2  -; #6 ff35d6b4461189846c6eb9e1fecfdda8  -; #7 c6da6180691decb6e365f5b5a222241c  -; #8 91f7aad51e10aafc550f0622d9662b2e  -. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
