# sources/user-network-fs/rclone/fs/log/logflags/logflags.go

## Purpose
`logflags.go` bridges logging options into pflag command-line flags.

## Important APIs, types, and functions
The only public function is `AddFlags(flagSet *pflag.FlagSet)`, which calls `flags.AddFlagsFromOptions` with `log.OptionsInfo`.

## Control flow
CLI setup passes a flag set to `AddFlags`; the generic config flag helper expands every entry in `log.OptionsInfo` into command-line flags.

## State and persistence behavior
The file holds no state. It wires flags to the global logging options handled by rclone's config system.

## Dependencies and integration points
It depends on `fs/config/flags`, `fs/log`, and `spf13/pflag`. It is used by command packages that expose global logging flags.

## Risks and edge cases
All behavior depends on `log.OptionsInfo` staying accurate. If option names or types change without corresponding flag handling, CLI logging configuration can drift.

## Test signals
No direct test is present. Coverage is indirect through CLI flag parsing and global option registration tests elsewhere.

Source-read signal: reviewed complete local file (13 lines). Functions/methods observed: `AddFlags`.
