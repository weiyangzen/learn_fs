# sources/security-integrity/gocryptfs/tests/reverse/exclude_test.go

## Purpose
Tests reverse-mode exclude and exclude-wildcard handling, including gitignore-style patterns, long names, negation, directory-only matches, anchors, and recursive globs.

## Important APIs, Types, And Functions
- `ctlsockEncryptPath` encrypts plaintext relative paths through the reverse control socket.
- `doTestExcludeTestFs` mounts with exclude flags, creates a synthetic tree, encrypts expected paths, and checks visibility.
- `directoryTree` models visible and hidden files and directories.
- `TestExcludeTestFs` and `TestExcludeAllOnlyDir1` define pattern sets and expected trees.

## Control Flow
For each pattern set, the test creates the backing tree after mounting, converts expected plaintext paths to encrypted names, adds `.name` companions for long encrypted names, and verifies hidden paths are absent while visible paths exist.

## State And Persistence
State is a temporary reverse filesystem and generated backing directory tree. The test relies on control-socket encryption to avoid embedding mode-specific encrypted names.

## Dependencies And Integration Points
Depends on `ctlsock`, `internal/nametransform`, reverse `newReverseFS`, and `test_helpers.VerifyExistence`.

## Risks And Edge Cases
Long-name exclusion has two artifacts: content and `.name`. Negation and anchored patterns can be easy to regress because visibility is checked in encrypted view rather than plaintext tree.

## Test Signals
Signals include absence of every hidden encrypted path, presence of every visible encrypted path, and coverage of both `-exclude-wildcard` and `-ew` aliases.
