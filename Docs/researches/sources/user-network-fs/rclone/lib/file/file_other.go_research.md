# sources/user-network-fs/rclone/lib/file/file_other.go

Source read signal: reviewed complete local file (20 lines, sha256 38a094c64d5890a0).

Purpose: Non-Windows implementation of file opening and reserved-name checking.

Important APIs/types/functions: Exposes `OpenFile = os.OpenFile` and `IsReserved(path string) error` returning nil.

Control flow: The standard library handles open semantics; reserved-name checking is a no-op outside Windows.

State and persistence behavior: Opening files may create/modify persistent files depending on flags; `IsReserved` is stateless.

Dependencies and integration points: Selected by `!windows` build tag. Shared `Open` and `Create` use this variable.

Risks and test signals: The variable form allows tests or callers in-package to replace `OpenFile`; no reserved-name validation is performed for non-Windows filesystems.
