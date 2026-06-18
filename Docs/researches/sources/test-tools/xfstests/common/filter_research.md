## sources/test-tools/xfstests/common/filter

Purpose: this is the generic output-normalization library for fstests. It removes host paths, device names, timing, UUIDs, version-dependent utility wording, block offsets, and other nondeterministic output so golden output comparisons remain stable.

Important APIs: `_within_tolerance` compares numeric values using `bc` and supports absolute or percent tolerances. Core path filters include `_filter_test_dir`, `_filter_scratch`, `_filter_testdir_and_scratch`, and `_filter_scratch_pool`. Command-specific filters include `_filter_dd`, `_filter_xfs_io`, `_filter_xfs_io_offset`, `_filter_xfs_io_error`, `_filter_xfs_io_fiemap`, `_filter_filefrag`, `_filter_quota`, `_filter_project_quota`, `_filter_quota_report`, `_filter_ro_mount`, `_filter_error_mount`, `_filter_busy_mount`, `_filter_mknod`, `_filter_mv`, `_filter_stat`, `_filter_touch`, `_filter_getcap`, `_filter_bash`, and `_filter_sysfs_error`. Attribute filters are split between `__filter_file_attributes` and `_filter_vfs_file_attributes`.

Control flow: most functions are simple stdin-to-stdout pipelines using `sed`, `awk`, `perl`, `grep`, or `tr`. The path filters intentionally replace longer mount paths before shorter device paths to avoid partial substitutions. Mount filters encode multiple historical util-linux message forms into a canonical message. File extent filters parse structured command output into compact machine-comparable tuples.

State and persistence: there is no durable state. `_within_tolerance` creates `$tmp.bc.1` and `$tmp.bc.2` and removes them. Several filters rely on global environment such as `TEST_DIR`, `TEST_DEV`, `SCRATCH_MNT`, `SCRATCH_DEV`, `SCRATCH_DEV_POOL`, `OVL_*`, `FSTYP`, `$AWK_PROG`, `$PERL_PROG`, and helper functions from `common/rc`.

Dependencies and integration: every test that emits environment-sensitive output can source this file. Btrfs tests in this subset use it to hide scratch/test paths, normalize xfs_io byte-rate summaries, and stabilize `dd`, `md5sum`, mount, and filesystem utility output.

Risks: the filters are regular-expression based and can over-filter if user data resembles device paths or error text. `_filter_size_to_bytes` assumes a one-character suffix and does not handle suffixless values. `_filter_xfs_io` has a broad sed pattern that may miss new units or format changes. `_filter_quota_report` uses environment-sensitive arithmetic and hidden root-file adjustments, so quota golden output depends on correct caller setup.

Test signals: these helpers are not normally tested directly; regressions show up as golden output diffs across util-linux/coreutils/xfsprogs/kernel versions. Stable expected output from the btrfs tests is a direct signal that the relevant filters still cover current tool wording.
