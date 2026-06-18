# sources/user-network-fs/rclone/backend/union/union_internal_test.go

Purpose: internal union tests for unexported state and subtle overlay behavior.

Important APIs: `MakeTestDirs`, `TestInternalReadOnly`, `InternalTest`, and `TestMoveCopy`.

Control flow/state: read-only test writes directly to a read-only upstream, reads through union, updates through union to create a writable shadow, removes it, and verifies the original read-only object reappears. Move/copy test builds local+memory union, checks feature exposure, then moves objects stored on each backend.

Dependencies/integration: rclone `fs/object/operations/fstest/fstests`, random helper, testify, and local runtime differences.

Risks/test signals: guards read-only update fallback and union `Move` enablement when underlying backends support either native move or copy/delete fallback.
