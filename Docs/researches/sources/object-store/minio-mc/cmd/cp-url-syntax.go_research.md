# sources/object-store/minio-mc/cmd/cp-url-syntax.go

Purpose: Validates command-line syntax for `mc cp` before transfers are prepared.

Important APIs/types/functions: `checkCopySyntax`.

Control flow: Requires at least two arguments, parses checksum flags, splits sources and target, rejects `--version-id` with multiple sources, rejects `--zip` with `--rewind`, ensures object-storage targets include a bucket, requires retention mode and duration to be paired, and rejects `--preserve` on Windows.

State and persistence: Stateless validation.

Dependencies/integration: Uses `newClientURL`, retention flag constants, `parseChecksum`, and fatal error helpers. Called by `mainCopy`.

Risks: Some validation is platform-specific and uses fatal exits, making it harder to unit test. Deeper source/target type validation happens later in URL preparation.

Test signals: No direct tests in this subset.
