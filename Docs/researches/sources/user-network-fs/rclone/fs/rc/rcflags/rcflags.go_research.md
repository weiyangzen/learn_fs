# sources/user-network-fs/rclone/fs/rc/rcflags/rcflags.go

## Purpose
This small package wires RC options into a `pflag.FlagSet` for command-line use.

## Important APIs, Types, and Functions
- `const FlagPrefix = "rc-"` names the flag namespace.
- `AddFlags(flagSet *pflag.FlagSet)` delegates to `flags.AddFlagsFromOptions` using `rc.OptionsInfo`.

## Control Flow
Callers provide a flag set; the helper adds every RC option described in `rc.OptionsInfo`, relying on the fs/config flag system for type conversion and option metadata.

## State and Persistence
No state is held in this file. Added flags later populate RC global options through the larger configuration pipeline.

## Dependencies and Integration Points
It depends on `fs/config/flags`, `fs/rc`, and `spf13/pflag`. It is an integration adapter between RC option metadata and the CLI.

## Risks and Edge Cases
The exported `FlagPrefix` is not used in `AddFlags`; the actual prefixing comes from option names already present in `OptionsInfo`. If RC option metadata changes, this helper inherits it automatically.

## Test Signals
No dedicated tests are in this subset. CLI flag behavior is indirectly covered where global option registration and flag parsing are tested elsewhere.
