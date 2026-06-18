# sources/sync-backup/rsync/testsuite/update_test.py

Purpose: validates `-u/--update` and `--force` decisions at depth, including a format-change case where a newer destination symlink should still be replaced by a source regular file.

Important APIs and flow: first creates a depth-3 tree, copies it, modifies a deep source file, makes the destination copy newer by mtime, and checks `rsync -a -u` preserves the destination content. It then makes destination older and expects an update. A second scenario creates source `foo` as a regular file and destination `foo` as a newer symlink; `-u` must replace the symlink. The final scenario sets source deep `f3` as a file and destination `f3` as a non-empty directory; without `--force` replacement must not happen, with `--force` it must.

State and persistence: each scenario resets `FROMDIR` and `TODIR`. Mtime manipulation uses `os.utime()`, including `follow_symlinks=False` for the symlink case.

Dependencies and integration: covers generator update decisions, file-type precedence, recursive parent handling, and forced deletion. Risks are filesystem mtime precision, mitigated by explicit offsets. Test signal is content preservation/update and file-type replacement at exact paths.
