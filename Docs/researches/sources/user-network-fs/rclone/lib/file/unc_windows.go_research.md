# sources/user-network-fs/rclone/lib/file/unc_windows.go

Source read signal: reviewed complete local file (31 lines, sha256 8b99fc56549604f7).

Purpose: Converts absolute Windows drive and server-share paths into extended-length UNC-style paths.

Important APIs/types/functions: Package regexp `isAbsWinDrive`; exported `UNCPath`.

Control flow: If a path starts with `\\?\`, it is already long and returned unchanged. If it starts with `\\`, it is converted to `\\?\UNC\...`; if it matches drive-root syntax such as `C:\`, it is prefixed with `\\?\`; otherwise it is unchanged.

State and persistence behavior: Stateless string conversion.

Dependencies and integration points: Uses `regexp` and `strings`. Called before Windows filesystem APIs where long paths or reserved characters may otherwise fail.

Risks and test signals: Regex only matches drive paths with a backslash after the colon, so relative drive paths are not converted. Tests assert idempotence and server/share behavior.
