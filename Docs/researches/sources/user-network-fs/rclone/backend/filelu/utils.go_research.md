# sources/user-network-fs/rclone/backend/filelu/utils.go

Purpose: This file contains a single utility for converting FileLu storage quota strings into byte counts.

Important APIs and types: `parseStorageToBytes(storage string) (int64, error)` parses a floating-point value from the string with `fmt.Sscanf` and multiplies it by 1024^3.

Control flow: `Fs.About` calls this helper for total and used storage strings from the account-info response.

State and persistence behavior: There is no state; it is a pure parser.

Dependencies and integration points: It depends on `fmt` and the assumption that FileLu account storage strings are numeric GB values.

Risks: Units are implicit and always treated as GiB, so strings with explicit units or different units would parse only the leading number and produce incorrect values. There are no tests for decimal, empty, or unit-suffixed inputs.

Test signals: No direct tests exist; `About` integration is the only coverage path.
