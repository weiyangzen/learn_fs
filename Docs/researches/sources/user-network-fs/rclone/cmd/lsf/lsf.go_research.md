# sources/user-network-fs/rclone/cmd/lsf/lsf.go

Purpose: implements `rclone lsf`, a script-friendly list command with configurable field order, separators, CSV mode, recursion, hash selection, IDs, encrypted names, tier, metadata, and absolute paths.

Important APIs/state: package globals `format`, `timeFormat`, `separator`, `dirSlash`, `recurse`, `hashType`, `filesOnly`, `dirsOnly`, `csv`, `absolute`; exported `Lsf(ctx, fsrc, out)`. `Lsf` builds `operations.ListFormat` and `operations.ListJSONOpt` from format characters.

Control flow: command validates one source, adjusts default separator to comma when `--csv` is used without explicit separator, then calls `Lsf`. `Lsf` maps each format rune to a ListFormat field and opt toggle; unknown runes return an error. It calls `operations.ListJSON` and prints one formatted item per line, normalizing directory size to `-1`.

State/persistence: no persistence; writes to provided writer. Risks include mutable package globals in tests and `timeFormat == "max"` rewriting the global. Dependencies include `operations.ListJSON`, hash types, and shared help. Test coverage is detailed for defaults, recursion, dir slash, format fields, separator, custom time, and max precision.
