## sources/sync-backup/bup/test/ext/test-drecurse

Purpose: verifies recursive directory listing order and exclude behavior for `bup drecurse`.

Important control flow: builds a small tree with files, directories, and a symlink, then compares output for base traversal, file/dir/symlink excludes, absolute path excludes, `--exclude-from`, and regex excludes for relative and absolute roots.

State and dependencies: temp repo and filesystem tree only; depends on `bup drecurse`.

Risks covered: postorder traversal expectations, directory trailing slash rendering, symlink handling, and consistency between literal and regex excludes.
