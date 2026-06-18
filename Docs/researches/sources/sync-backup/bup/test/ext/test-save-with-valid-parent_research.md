<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-with-valid-parent -->
# sources/sync-backup/bup/test/ext/test-save-with-valid-parent

Purpose: regression test for saving a path whose parent directory is already up to date in the index. Important APIs are `bup index`, `save`, `restore`, and `compare-trees`. Control flow creates a nested source tree, indexes it, saves a child path with an up-to-date parent, then restores and compares the result to ensure parent validity does not suppress the requested child save. State is the bup index validity state, branch tree, and restored directory. Dependencies are WvTest and compare-trees. Risks are optimization logic skipping traversal when a parent is marked valid, producing incomplete saves. Test signal is restored tree equality with the original requested subtree.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-with-valid-parent -->
