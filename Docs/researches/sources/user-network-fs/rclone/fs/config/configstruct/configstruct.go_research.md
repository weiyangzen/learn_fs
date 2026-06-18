# sources/user-network-fs/rclone/fs/config/configstruct/configstruct.go

Purpose: maps unstructured config maps into typed option structs and back through string conversion, using reflection and config tags.

Important APIs/types/functions: `camelToSnake`, `StringToInterface`, `InterfaceToString`, `Item`, `Items`, `Set`, `SetAny`, plus helpers `setValue` and `setIfSameType`. Supported built-ins include strings, numeric types, bool, `time.Duration`, `[]string`, and custom types implementing `Set(string) error` or `fmt.Stringer`.

Control flow: `Items` requires a pointer to a struct, iterates exported fields, uses `config` tags or CamelCase-to-snake conversion, skips `config:"-"`, recursively expands nested structs unless the field's address implements `Set`, and returns setters that write reflected values back. `Set` reads string config values and parses them into field types. `SetAny` first assigns values that already match the field type, otherwise stringifies the input and reparses it. Empty string parse errors are masked so empty config is treated like unset for non-string types.

State and persistence behavior: no global state. The target struct is mutated in place. Returned `Item.Set` closures capture struct fields and should be used while the original value remains valid.

Dependencies and integration points: used by option registration/config loading to fill `ConfigInfo` and backend option structs from `configmap.Getter` or rc maps. Depends on `encoding/csv`, reflection, time parsing, and configmap.

Risks: reflection panics are possible with unexported fields because `field.Addr().Interface()` requires interfaceable values; comments require public fields. Nested structs with `Set` are treated as scalar config items, which is important for rclone flag types. CSV handling for `[]string` must remain aligned with config syntax.

Test signals: configstruct tests cover item discovery, nested structs, tags, setting values, `SetAny`, conversions, error messages, and camel-to-snake internals.
