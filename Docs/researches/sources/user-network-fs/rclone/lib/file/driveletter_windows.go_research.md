# sources/user-network-fs/rclone/lib/file/driveletter_windows.go

Source read signal: reviewed complete local file (22 lines, sha256 87e703cc3e18f250).

Purpose: Finds an available Windows drive letter for mount-like operations.

Important APIs/types/functions: Exports `FindUnusedDriveLetter() uint8`.

Control flow: Iterates from `Z:` down to `D:`, skipping `A:`, `B:`, and normally-system `C:`, and returns the first letter whose root path does not exist.

State and persistence behavior: Reads filesystem mount state via `os.Stat`; no state is written.

Dependencies and integration points: Uses `os` and Windows build tag. Consumers can use the returned byte to choose a mount drive.

Risks and test signals: Race exists between discovery and later mount. Access errors other than not-exist are treated as unavailable, and substituted network drives may influence results.
