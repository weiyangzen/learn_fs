# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/util/test_helper.go

Purpose: shared emulator test helper library for starting proxy servers, killing them, timing write sync/read operations, and parsing timeout flags.
Important APIs/functions: `StartProxyServer`, `KillProxyServerProcess`, `WriteFileAndSync`, `ReadFirstByte`, `GetChunkTransferTimeoutFromFlags`, `GetChunkRetryDeadlineFromFlags`, and private `getPortAndProcessInfoFromLogFile`. Constant `PortAndProxyProcessIdInfoRegex` parses proxy log output.
Control flow: `StartProxyServer` runs the proxy with `go run`, polls its log for listening port/PID, and sets `STORAGE_EMULATOR_HOST` to the proxy. Kill unsets the env var and sends SIGINT. Timing helpers create/read files and measure only `Sync` or first `Read`. Flag parsers scan string flags with defaults.
State and persistence: mutates process environment, starts a background process, reads proxy log files, and creates mounted files. Random data is generated for write tests.
Dependencies and integration points: imported by read/write stall, gRPC header, and streaming-write failure tests. Depends on `operations` helpers, OS process APIs, regex polling, and expected proxy log format.
Risks and edge cases: `STORAGE_EMULATOR_HOST` lacks `http://` when set to localhost port, matching Go storage client expectations but easy to misuse. `go run` startup polling can fail if logs are delayed.
Test signals: helper success returns port/PID, elapsed durations, and parsed timeout values; failures usually indicate proxy startup/log-format/environment issues.
