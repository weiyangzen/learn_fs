# sources/user-network-fs/rclone/fs/config/configstruct/configstruct_test.go

Purpose: externally tests the reflection-based config struct mapper and string conversion helpers.

Important APIs/types/functions: local structs `Conf`, `Conf2`, and `ConfNested` exercise plain fields, config tags, numeric/bool/duration/size suffix types, embedded structs, nested tagged structs, and a struct-like scalar `fs.Tristate`. Tests include `TestItemsError`, `TestItems`, `TestItemsNested`, `TestSetBasics`, `TestSetMore`, `TestSetFull`, `TestSetAnyFull`, `TestStringToInterface`, and `TestInterfaceToString`.

Control flow: item tests clean closure fields before comparing expected metadata. Set tests apply simple getter maps or `map[string]any` values and compare fully populated structs. Conversion tests are table-driven and assert exact values or exact wrapped error strings.

State and persistence behavior: no persistence; target structs are mutated in memory. Tests document that absent config preserves defaults and that empty arrays encode as empty strings while `[]string{""}` encodes as `""`.

Dependencies and integration points: imports `fs.Duration`, `fs.SizeSuffix`, and `fs.Tristate`, making sure custom rclone types work with the generic mapper. Uses `testify`.

Risks: exact error strings can be sensitive to upstream parser changes. Tests do not cover unexported fields or `config:"-"` in this file.

Test signals: strong behavioral coverage for type conversion, nested item naming, and default preservation.
