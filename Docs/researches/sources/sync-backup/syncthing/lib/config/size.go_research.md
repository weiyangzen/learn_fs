# sources/sync-backup/syncthing/lib/config/size.go

## sources/sync-backup/syncthing/lib/config/size.go

Purpose: Represents user-configurable sizes and percentages, and checks free-space thresholds.

Important APIs/types/functions: `Size` has `Value` and `Unit`; functions/methods include `ParseSize`, `BaseValue`, `Percentage`, `String`, `ParseDefault`, `CheckFreeSpace`, internal `checkAvailableSpace`, and `formatSI`.

Control flow and state: Parsing trims whitespace, accepts decimal/comma numeric characters, then treats the remaining suffix as the unit. `BaseValue` multiplies by SI prefix k/m/g/t, and `Percentage` checks for `%` anywhere in the unit. Free-space checks compare either free percentage or absolute free bytes; `checkAvailableSpace` first reserves the requested bytes before checking the minimum.

Dependencies and integration: Uses `fs.Usage`. `FolderConfiguration.MinDiskFree`, `OptionsConfiguration.MinHomeDiskFree`, and folder free-space checks depend on it.

Risks and test signals: Negative values fail parse because `-` is not accepted in the numeric prefix. Prefix-plus-percent strings are accepted even if nonsensical. `size_test.go` covers parsing, defaults, SI formatting, and available-space checks.
