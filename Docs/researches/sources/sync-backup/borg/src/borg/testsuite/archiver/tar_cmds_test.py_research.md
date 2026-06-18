<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tar_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/tar_cmds_test.py

Purpose: integration coverage for `export-tar` and `import-tar`, including GNU/gzip compatibility, hardlinks, path normalization, concatenated tars, Borg/PAX metadata, xattrs, and POSIX ACLs.

Important APIs: `cmd`, `assert_dirs_equal`, `changedir`, `create_test_files`, `create_regular_file`, `_extract_hardlinks_setup`, `requires_hardlinks`, GNU tar/gzip probes, xattr helpers, `acl_get`, `acl_set`, and platform ACL skip markers.

Control flow: export tests create Borg archives, export tar/tar.gz with format/list/strip flags, extract via GNU tar, and compare trees. Import tests feed normal, gzip, unusual-path, dotdot, dotslash, and concatenated tar archives into Borg, then list or extract results. Roundtrip tests export/import Borg and PAX formats and verify xattrs/ACLs survive.

State and persistence: creates tar files in the workdir, repositories, extracted outputs, xattrs, ACLs, and hardlink relationships. Some tests intentionally remove flag files or tar intermediates before comparisons.

Dependencies/integration: depends on external GNU tar/gzip, filesystem xattrs/ACLs, hardlinks, platform-specific path and permission behavior, and archive metadata encoding. Risks include tar path traversal handling, metadata loss, brittle external tool availability, and exact tree comparison semantics. Test signals are directory equality, link counts, path lists, expected ValueError for `..`, xattr values, and ACL byte strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tar_cmds_test.py -->
