# sources/user-network-fs/rclone/fs/registry_test.go

## Purpose
This file tests filesystem option metadata and configuration getter behavior.

## Important APIs, Types, and Functions
- Tests cover `Option` as a `pflag.Value`, `Options.setValues`, `Get`, `Overridden`, `NonDefault`, JSON marshaling, `GetValue`, `String`, `Set`, `Type`, `FlagName`, `EnvVarName`, config/environment getters, and `Options.NonDefaultRC`.
- Shared fixtures define `nouncOption`, `copyLinksOption`, `caseInsensitiveOption`, and `testOptions`.

## Control Flow
Tests construct options and config maps, set/unset environment variables, monkey-patch `ConfigFileGet`, and assert getter priority and returned values. `NonDefaultRC` tests use small tagged structs to verify field-name output and missing-key errors.

## State and Persistence
The test temporarily mutates process environment variables and the package-level `ConfigFileGet` function, restoring them with defers. It does not persist files.

## Dependencies and Integration Points
It uses `configmap`, `pflag`, `testify`, and option parsing through `configstruct.StringToInterface`. It protects behavior consumed by CLI flags, env/config loading, RC option output, and backend registration.

## Risks and Edge Cases
Environment and global function mutation mean tests should not be parallelized casually. The tests assert JSON text for option marshaling and therefore encode field ordering/format expectations.

## Test Signals
Coverage is good for user-visible option stringification/parsing and config priority behavior. It does not directly cover backend alias registration or reverse `FindFromFs` lookup.
