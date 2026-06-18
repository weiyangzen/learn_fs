# sources/user-network-fs/rclone/cmd/serve/docker/options.go

## Purpose

`options.go` maps Docker volume creation options into rclone backend, mountlib, and VFS configuration.

## Important APIs, Types, and Functions

`Volume.applyOptions` handles special keys `remote`/`fs`, `type`, `path`, `mount-type`, and `persist`, stores remaining options, identifies backend type, parses backend configuration, and applies mount/VFS options. `normalOptName` normalizes option spelling.

## Control Flow

The function copies driver defaults, parses the remote or backend type, resolves explicit path override, finds backend metadata, classifies each remaining option as special, mount, VFS, or backend option, parses typed mount/VFS maps with `configstruct.Set`, builds `vol.fsString`, and validates the volume.

## State and Persistence Behavior

It mutates the `Volume` fields that are saved into JSON state: `Fs`, `Type`, `Path`, `Options`, plus runtime-only `fsString`, `persist`, and `mountType`.

## Dependencies and Integration Points

It integrates Docker's flat option map with rclone `fspath.Parse`, backend registry, `fs.ConfigMap`, `rc.Params`, mountlib `OptionsInfo`, VFS `OptionsInfo`, and configstruct parsing.

## Risks and Test Signals

Risks include option-name collisions, backend prefix stripping surprises, unsupported backend option rejection, and sensitive option persistence in driver state. `options_test.go` covers normalization, mount/VFS/backend classification, and parse errors.
