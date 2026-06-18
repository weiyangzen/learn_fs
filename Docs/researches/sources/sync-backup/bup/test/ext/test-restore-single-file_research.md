<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-restore-single-file -->
# sources/sync-backup/bup/test/ext/test-restore-single-file

Purpose: regression test for restoring a single file path from a save into an empty destination. Important APIs are `bup init`, `index`, `save -n`, `tick`, and `restore -C`. Control flow creates `foo/bar` and `foo/baz`, indexes the `foo` directory, saves it as branch `foo`, advances bup time, then restores only `baz` through a full VFS path. State is the small temp tree, the saved branch, and the restore directory. Dependencies are WvTest and normal bup path resolution. Risks are off-by-one path handling for a file target versus a directory target, especially when the save path includes the tempdir prefix. Test signal is successful restore command completion for the requested single file.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-restore-single-file -->
