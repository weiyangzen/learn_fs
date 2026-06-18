# sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main_test.go

Purpose: unit tests for mount-helper option translation and device parsing.

Important APIs/types/functions: `TestMakeGcsfuseArgs` and `TestParseArgs_DeviceIsParsedCorrectly`.

Control flow: table-driven tests check boolean flags with underscores/hyphens, string flags, debug flags, ignored mount options, pass-through regular options, mixed options, and `o` as a literal option. Device tests ensure path-like bucket names are reduced to their base name.

State/persistence behavior: pure unit tests; no mount process is started.

Dependencies/integration: depends on `testify/assert` and current gcsfuse flag definitions from `cfg.BuildFlagSet`.

Risks/test signals: uses `assert.ElementsMatch` for generated flags because option map order is not stable; this does not validate exact argument ordering before bucket/mount point.
