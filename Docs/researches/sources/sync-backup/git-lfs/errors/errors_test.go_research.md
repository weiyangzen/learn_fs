<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors_test.go -->
# sources/sync-backup/git-lfs/errors/errors_test.go

## Research

This test file validates high-level behavior of the custom error system. It confirms plain Go errors do not satisfy LFS behavior checks, wrapped fatal errors do, nested behavior wrappers preserve both outer and inner markers, and context helpers are inert for plain errors but functional for wrapped errors.

The tests are pure and exercise the recursive behavior inspection path in `types.go` plus context helpers in `context.go`. Gaps include joined errors, retriable URL errors, Retry-After parsing, protocol/auth/smudge/clean constructors, `ExitStatus`, and stack formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors_test.go -->
