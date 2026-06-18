# sources/user-network-fs/rclone/lib/file/driveletter_other.go

Source read signal: reviewed complete local file (8 lines, sha256 38c2aba3f2ad97d0).

Purpose: Provides the non-Windows stub for unused drive-letter discovery.

Important APIs/types/functions: Exports `FindUnusedDriveLetter() uint8`, returning zero.

Control flow: No platform work is done on non-Windows builds.

State and persistence behavior: Stateless.

Dependencies and integration points: Selected by `!windows` build tag so callers can use one API cross-platform.

Risks and test signals: Callers must interpret zero as no drive letter available. Build tags are the main correctness surface.
