# sources/sync-backup/borg/src/borg/testsuite/archiver/extract_cmd_test.py

Purpose: comprehensive integration tests for `borg extract`: symlink/hardlink restoration, directory timestamp repair, atime/birthtime, sparse files, filename/pattern handling, strip-components, xattrs/capabilities, overwrite behavior, continue/resume extraction, missing chunk handling, existing directory preservation, dry-run listing, and post-y2038 timestamps.

Important APIs/types/functions: tests use shared helpers `cmd`, `create_test_files`, `create_regular_file`, `assert_dirs_equal`, `_extract_hardlinks_setup`, `assert_creates_file`, `open_archive`, and `create_src_archive`. They also use xattr/platform APIs, `has_seek_hole`, `same_ts_ns`, `granularity_sleep`, `flags_noatime`, `BackupPermissionError`, `bin_to_hex`, and `get_birthtime_ns`.

Control flow: early tests create archives with symlinks, hardlinked symlinks, directories/files in different archive orders, atime/birthtime metadata, and sparse files, then extract and compare metadata/content. Include/exclude tests combine positional patterns, fnmatch/regex, `--exclude`, `--exclude-from`, and `--pattern`. Output tests verify default/info/list/progress behavior. Xattr tests patch setters to simulate E2BIG/ENOTSUP/EACCES, preserve Linux capabilities under patched chown, handle percent signs, and macOS resource forks. Overwrite tests verify replacing existing file/dir targets but warning on non-empty directory conflicts. `--continue` simulates partial extraction and checks which files/directories are reused or re-extracted. Missing chunk test deletes a referenced object and expects zero-byte substitution warning. Existing directory and year-2261 tests guard specific filesystem behaviors.

State and persistence behavior: creates repositories/archives, output trees, hardlinks, symlinks, sparse files, xattrs, flags, timestamps, and direct repository object deletion. Some tests patch OS/xattr functions in-process. `--continue` relies on existing output directory state.

Dependencies and integration points: covers extract command, archive item restoration, platform metadata APIs, pattern engine, repository object retrieval fallback, hardlink map behavior, sparse extraction, xattr/capability handling, and local/remote/binary variants.

Risks: highly platform-sensitive around symlink/hardlink support, Darwin/FreeBSD flags, fakeroot xattrs, sparse-file detection, Windows ctime, and filesystem timestamp range. Missing chunk behavior currently returns success-like output with zeros, noted as a TODO in the test.

Test signals: broad end-to-end extraction correctness signals through metadata comparisons, exact restored contents, warning/exit-code checks, and preservation of tricky filesystem features.
