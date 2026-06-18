# sources/sync-backup/restic/internal/fs/node_xattr_test.go

Purpose: Tests xattr permission-error classification on POSIX-like xattr platforms.

Important APIs: `TestIsListxattrPermissionError`.

Control flow and state: Creates synthetic `xattr.Error` values, passes them through `handleXattrErr`, and checks whether `isListxattrPermissionError` recognizes only list-permission failures.

Dependencies and integration: Supports `nodeFillExtendedAttributes(ignoreListError=true)` behavior.

Risks: Only synthetic errors are tested; real filesystem permission behavior is covered indirectly elsewhere.

Test signals: Confirms the backup option to ignore xattr list permission errors targets the intended error shape.
