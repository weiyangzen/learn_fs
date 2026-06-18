# sources/user-network-fs/rclone/fs/registry.go

## Purpose
This file implements rclone's filesystem backend registry and option metadata system used by backends, global options, config, flags, environment variables, and RC option reporting.

## Important APIs, Types, and Functions
- `RegInfo` describes a backend: name, description, prefix, constructors, config callback, options, aliases, command help, visibility, and metadata.
- `Options` is a slice of `Option` with helpers `Add`, `AddPrefix`, `setValues`, `Get`, `SetDefault`, `Overridden`, `NonDefault`, `NonDefaultRC`, and `HasAdvanced`.
- `Option` describes a config/flag/API option and implements pflag-style methods: `String`, `Set`, `Type`.
- `OptionExample` and `OptionExamples` model selectable examples.
- `Register`, `Find`, and `MustFind` manage backend registration and lookup.
- `OptionsInfo`, `OptionsRegistry`, `RegisterGlobalOptions`, `GlobalOptionsInit`, and `OptionsInfo.Check/load` manage global option blocks.
- `Type`, `addReverse`, and `FindFromFs` support reverse lookup from an `fs.Fs` instance to its registration.

## Control Flow
Backends call `Register` from init functions. Registration fills default option values, sets a default prefix, appends the common `description` option, and creates hidden alias registrations. Global option registration validates option metadata against struct `config` tags, loads defaults/env values immediately, and can call reload hooks. `GlobalOptionsInit` reloads all option blocks in deterministic order with `main` first.

## State and Persistence
`Registry`, `OptionsRegistry`, and `typeToRegInfo` are process-global mutable registries. The file itself does not write config files, but it reads through configmap/configstruct layers and environment/config getters elsewhere.

## Dependencies and Integration Points
It depends on `configmap`, `configstruct`, `errcount`, reflection, sorting, and string normalization. It is foundational for all backend packages, RC option declaration, command-line flags, environment variable mapping, and config UI/API output.

## Risks and Edge Cases
`Registry` is not protected by a mutex, assuming init-time registration. `Register` mutates `RegInfo.Options` by appending `description`, so callers should not assume their original slice remains unchanged. `Option.Set` for string arrays relies on reflect pointer behavior and assumes defaults are slice-like. `OptionsInfo.Check` logs type mismatches without adding them to the returned errcount, so some metadata issues may be non-fatal.

## Test Signals
`registry_test.go` covers option string/type/set behavior, defaults, overridden/non-default detection, JSON marshaling, flag/env names, environment/config getter priority, and `NonDefaultRC` success/error cases.
