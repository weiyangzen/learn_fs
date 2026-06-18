## sources/test-tools/xfstests/tests/btrfs/005

Purpose: this online defragmentation test checks file, directory, and filesystem defrag paths, including compressed defrag and invalid/edge range arguments.

Important local APIs: `_create_file mode` writes a fragmented file backward and records its md5sum. `_btrfs_online_defrag object range compress` builds `btrfs filesystem defragment` options and tolerates historical return code 20 as success. `_checksum` validates the md5sum. `_setup_defrag`, `_cleanup_defrag`, and `_rundefrag` compose mkfs, mount, file creation, defrag, checksum, unmount, and fs check.

Control flow: it first verifies scratch and defrag support, then runs a matrix: single file default with compression off/on; single file invalid negative start; start beyond EOF; negative length; length beyond file size; partial length; directory defrag; and whole filesystem defrag.

State and persistence: scratch is reformatted for each matrix row. `/tmp/checksum` is a global checksum side effect outside `$tmp`, which is a legacy risk. `$seqres.full` captures defrag diagnostics.

Dependencies: `common/defrag`, `$BTRFS_UTIL_PROG`, `_require_defrag`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_cycle_mount`, `_check_scratch_fs`, `md5sum`, and `dd`.

Risks: storing checksum at `/tmp/checksum` can conflict with parallel tests. Cases labelled "should fail" do not require the command to fail; they only report unexpected non-success based on return code, so golden output captures behavior. Range option semantics can vary with btrfs-progs versions.

Test signals: printed matrix labels and no checksum failures are expected. Regressions show as `btrfs filesystem defragment failed!`, `md5 checksum failed!`, or scratch fs check failures.
