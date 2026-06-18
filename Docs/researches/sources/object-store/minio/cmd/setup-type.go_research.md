# sources/object-store/minio/cmd/setup-type.go

Purpose: This file defines the enum describing the server deployment/storage setup mode and maps it to MinIO mode strings for logging, startup behavior, and feature decisions.

Important APIs and types: `SetupType` is an `int` enum with `UnknownSetupType`, `FSSetupType`, `ErasureSDSetupType`, `ErasureSetupType`, and `DistErasureSetupType`. Its `String` method maps known values to `globalMinioModeFS`, `globalMinioModeErasureSD`, `globalMinioModeErasure`, or `globalMinioModeDistErasure`, falling back to `"unknown"`.

Control flow: The only logic is the switch in `String`. Other code, notably endpoint creation and `serverHandleCmdArgs`, sets global booleans from this enum.

State and persistence behavior: There is no mutable state or persistence. The enum value is runtime classification derived from command/config endpoints.

Dependencies and integration points: It is consumed by server startup, mode reporting, setup validation, and any code that branches on filesystem, single-drive erasure, local erasure, or distributed erasure behavior.

Risks: Adding a new setup type requires updating `String` and all global-mode branching. Unknown values degrade to `"unknown"`, which avoids panics but may hide unsupported state if not validated earlier.

Test signals: There are no direct tests here. Indirect signals come from server startup tests and mode-specific integration runs in `server_test.go`.
