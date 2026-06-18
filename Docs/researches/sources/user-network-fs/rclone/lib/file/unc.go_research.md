# sources/user-network-fs/rclone/lib/file/unc.go

Source read signal: reviewed complete local file (10 lines, sha256 ba84bc8ce489fc19).

Purpose: Non-Windows stub for converting Windows paths to long UNC paths.

Important APIs/types/functions: Exports `UNCPath(l string) string`.

Control flow: Returns the input unchanged.

State and persistence behavior: Stateless.

Dependencies and integration points: Selected by `!windows` build tag so callers can use `UNCPath` cross-platform.

Risks and test signals: No risk beyond build-tag correctness; Windows behavior is tested separately.
