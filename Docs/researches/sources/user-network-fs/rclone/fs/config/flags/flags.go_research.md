<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/flags/flags.go -->
# sources/user-network-fs/rclone/fs/config/flags/flags.go

## Purpose
Wraps `spf13/pflag` with rclone-specific environment-variable defaults, option-to-flag conversion, and documentation grouping.

## Important APIs, Types, And Control Flow
`Groups` and `Group` collect flag sets by named categories. `installFlag` locates a flag, reads its `RCLONE_*` environment default, applies special CSV parsing for `[]string` `fs.Option` values, updates `DefValue`, and registers global flags into `All`. Wrapper functions (`StringP`, `BoolP`, `DurationP`, `VarP`, `StringArrayP`, `CountP`, etc.) create flags then call `installFlag`. `AddFlagsFromOptions` converts `fs.Options` into pflag values, trims help to the first sentence, marks password flags as obscured, sets bool `NoOptDefVal`, and respects command-line hiding.

## State And Persistence
Global `All` is initialized with standard documentation groups. Runtime state is pflag registration plus process environment-derived defaults; no files are persisted.

## Dependencies And Integration Points
Integrates pflag, `fs.Option`, `fs.CommaSepList`, option hiding, environment naming, and rclone command documentation grouping.

## Risks And Test Signals
Unknown groups and malformed env values are fatal, so command initialization can abort early. Duplicate option names are skipped/logged. Risk areas are env CSV quoting for arrays, prefix/no-prefix lookup consistency, and global mutation during tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/flags/flags.go -->
