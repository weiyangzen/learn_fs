<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors.go -->
# sources/sync-backup/git-lfs/errors/errors.go

## Research

`errors.go` is the public entrypoint for Git LFS error construction. It wraps `github.com/pkg/errors` for stack-bearing `New`, `Errorf`, `Wrap`, and `Wrapf`, provides `Join` through the standard library, and recursively unwraps `Cause`.

The control flow in `Wrap`/`Wrapf` creates `wrappedError` values from `types.go`, preserving context support and behavioral marker methods. `Wrapf(nil, ...)` creates an empty underlying error. There is no persistent state. Integration is broad across Git LFS packages for fatal, auth, smudge, retriable, and protocol errors. Risks include mixed unwrap models (`pkg/errors.Cause`, standard `errors.Join`, and custom `parentOf`), nil wrapping behavior, and stack formatting compatibility. Tests in `errors_test.go` validate behavior marker detection and context interactions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors.go -->
