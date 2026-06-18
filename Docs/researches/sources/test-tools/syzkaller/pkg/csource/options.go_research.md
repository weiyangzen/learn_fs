# sources/test-tools/syzkaller/pkg/csource/options.go

This file defines and validates csource generation options, serializes/deserializes option payloads, handles legacy dashboard formats, parses manual feature flags, and converts feature negotiation into executor environment flags.

The main type is `Options`, containing execution topology, sandbox, leak checking, network/device setup, filesystem/environment setup, tracing, comments, and embedded `LegacyOptions`. `Check` validates cross-option constraints such as collide requiring threaded mode, procs/net reset/repeat-times requiring repeat, sandbox-required setup options, namespace requiring tmpdir, cgroups requiring tmpdir, and OS-specific Linux-only restrictions. `DefaultOpts` derives manager defaults from `mgrconfig.Config`.

Persistence is JSON serialization through `Serialize` and `DeserializeOptions`; legacy parser support reads older struct-like strings and old JSON keys so dashboard reproducers remain usable. `ParseFeaturesFlags`, `PrintAvailableFeaturesFlags`, `FeaturesToFlags`, and `FlatRPCFeaturesToCSource` bridge manual enable/disable names with `flatrpc` feature and execution environment bits.

Dependencies include JSON, reflection-friendly comparable option structs, manager config, flatrpc enums, and target OS constants. Integration points are syz-manager default repro generation, dashboard-stored reproducers, executor feature negotiation, and csource tests. Risks include backwards compatibility with legacy fields, invalid option combinations creating uncompilable C, feature-name drift between flatrpc and csource, and non-Linux option leakage. Tests in `options_test.go` cover round trips, canned legacy values, valid option enumeration, and feature flag parsing.
