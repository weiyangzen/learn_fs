# sources/user-network-fs/gcsfuse/cmd/legacy_main_test.go

## Purpose
`legacy_main_test.go` tests non-FUSE helper behavior in `legacy_main.go`. It focuses on storage handle creation, user-agent construction, dynamic mount classification, recursive metadata prefetch helper behavior, and environment forwarding for daemonized runs.

## Important APIs And Test Structure
The suite uses `testify/suite` with `MainTest`. Tests create storage handles using test credentials for HTTP/1, gRPC, and gRPC in GKE mode. User-agent tests cover `GCSFUSE_METADATA_IMAGE_TYPE`, app name presence, mount ID, and a six-bit config string describing file cache, range-read cache, parallel downloads, streaming writes, buffered reads, and profile usage. Other tests cover `callListRecursive`, `isDynamicMount`, `fsName`, and `forwardedEnvVars`.

## Control Flow And State
Tests manipulate process environment with `t.Setenv`, create temporary directories/files for recursive walking, and inspect returned string slices for forwarded env vars. They do not daemonize or mount. `TestForwardedEnvVars_AlwaysPresent` checks PATH, HOME, parent process directory, background marker, and mount UUID; precedence tests ensure `https_proxy` wins over `http_proxy`; inclusion tests cover GCE metadata, Google credentials, gRPC logging, and `no_proxy`; exclusion tests ensure unset optional variables are not forwarded.

## Dependencies And Integration
The file integrates cfg config structs, common versioning, logger environment keys, util parent-directory key, metrics no-op handle, and storage handle creation. Its assertions document externally visible telemetry and daemon environment contracts that `Mount` depends on.

## Risks And Test Signals
The tests give good signal for helper-level compatibility but avoid actual daemonize/fuse behavior. Storage handle tests may be sensitive to credential testdata shape and storage client constructor behavior. The user-agent tests encode exact formatting, so they catch telemetry regressions but can be brittle for intentional format changes. Environment tests are important because missing forwarded variables can break auth, proxying, metadata mocks, gRPC diagnostics, or relative path resolution in background mode.
