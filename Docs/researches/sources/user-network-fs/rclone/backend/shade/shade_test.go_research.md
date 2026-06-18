# sources/user-network-fs/rclone/backend/shade/shade_test.go

Purpose: external integration test entry point for the Shade backend.

Important APIs/types/functions: `TestIntegration` runs `fstests.Run` against remote `TestShade:` with `NilObject: (*shade.Object)(nil)`, skips invalid UTF-8 tests, and sets `eventually_consistent_delay` to 7.

Control flow: the generic rclone test suite exercises backend operations on a configured Shade drive. The extra config acknowledges eventual consistency in the service.

State and persistence behavior: creates/deletes remote Shade objects and may interact with backend token persistence through normal initialization. Local state is owned by the test harness.

Dependencies/integration: imports `shade` as an external package and rclone `fstests`.

Risks/test signals: useful broad signal for API behavior, but depends on live credentials/service availability and does not isolate token, directory cache, or multipart edge cases.
