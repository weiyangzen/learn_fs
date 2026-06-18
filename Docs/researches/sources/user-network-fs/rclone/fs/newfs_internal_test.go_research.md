# sources/user-network-fs/rclone/fs/newfs_internal_test.go

## Purpose
`newfs_internal_test.go` tests the internal `addConfigToContext` behavior for connection-string `override.` and `global.` config keys.

## Important APIs, types, and functions
Tests target `addConfigToContext`, `WithRCRequest`, and `GetConfig` behavior for context-local and global config mutation. `configmap.Simple` supplies synthetic keys such as `override.user_agent` and `global.user_agent`.

## Control flow
The suite covers no-change, override-only, global-only, and global-from-rc cases. It compares whether the returned context is the original or a new one, checks user-agent values on the returned context, and verifies whether the process-wide config was or was not mutated.

## State and persistence behavior
Tests mutate the global config's `UserAgent` for global-only cases and restore it with `defer`. Context-local config is created via `AddConfig`.

## Dependencies and integration points
It depends on rclone config option metadata, `configstruct.Set`, and rc request marking. It protects `NewFs` behavior for remote-control requests and ordinary CLI backend startup.

## Risks and edge cases
Global config leakage is the main risk: rc requests must not change process-wide settings, while CLI global overrides intentionally do. Tests only cover `user_agent`, so type conversion issues for other options rely on shared configstruct tests.

## Test signals
The tests provide direct regression coverage for context identity, override scoping, global mutation, and rc isolation.

Source-read signal: reviewed complete local file (77 lines). Functions/methods observed: `TestAddConfigToContext_NoChanges`, `TestAddConfigToContext_OverrideOnly`, `TestAddConfigToContext_GlobalOnly`, `TestAddConfigToContext_GlobalFromRC`.
