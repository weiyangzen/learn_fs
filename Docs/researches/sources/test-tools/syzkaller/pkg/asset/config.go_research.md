# sources/test-tools/syzkaller/pkg/asset/config.go

## Purpose
Defines asset upload configuration and validation.

## Important APIs, Types, and Functions
`Config` controls debug tracing, upload destination, deprecation, public access, and per-asset `TypeConfig`. `TypeConfig.Validate`, `Config.IsEnabled`, `Config.IsEmpty`, and `Config.Validate` are the public helpers.

## Control Flow
Validation checks every configured asset type is known, validates its type config, rejects non-empty asset settings without `upload_to`, and permits only `gs://` or `dummy://` upload destinations.

## State and Persistence Behavior
Configuration data is loaded by callers and held in memory. No writes.

## Dependencies and Integration Points
Depends on dashboard asset type constants and `GetTypeDescription`. Consumed by `StorageFromConfig` and upload gating.

## Risks and Test Signals
Risk is nil `Config` method calls except `IsEmpty`; `IsEnabled` expects non-nil config. Storage tests cover disabled asset behavior and supported dummy destination.
