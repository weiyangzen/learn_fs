## sources/sync-backup/kopia/fs/ignorefs/resolve_test.go

Purpose: targeted internal-package regression test for symlink loop handling in ignore-file resolution.

Important APIs/types/functions: `TestNoInfiniteResolveLink` constructs a three-link cycle and calls unexported `resolveSymlink`.

Control flow, state, and persistence: the test uses `mockfs` symlinks `a -> b -> c -> a`, resolves one link, and asserts the resolver returns `errTooManySymlinks` with no file. It uses only in-memory state.

Dependencies and integration points: depends on `fs.Symlink`, `mockfs`, and test logging contexts. It validates a safety path that is reachable when dot-ignore files are symbolic links.

Risks and test signals: protects against infinite traversal and stack/resource exhaustion. It does not test successful resolution because those cases are covered in the broader ignorefs tests.
