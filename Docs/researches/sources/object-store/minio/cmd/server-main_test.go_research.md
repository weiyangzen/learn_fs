# sources/object-store/minio/cmd/server-main_test.go

Purpose: This file contains focused tests for server configuration-file parsing and object-layer initialization. It protects `mergeServerCtxtFromConfigFile` compatibility with bundled YAML fixtures and verifies that `newObjectLayer` produces the erasure server-pool implementation for supported local disk counts.

Important APIs and types: `TestServerConfigFile` uses `mergeServerCtxtFromConfigFile`, `serverCtxt`, and expected `Layout.pools` hashes. `TestNewObjectLayer` uses `getRandomDisks`, `removeRoots`, `mustGetPoolEndpoints`, `newObjectLayer`, and checks the returned object with `reflect.TypeOf` / type assertion to `*erasureServerPools`.

Control flow: The config test iterates valid and invalid fixture paths, expects errors for invalid YAML/type/disk layouts, and for valid fixtures asserts that two pools were parsed and the first pool's stable hash matches the fixture expectation. The object-layer test creates temporary disk paths for a single-drive backend, initializes the layer, validates its concrete type, then repeats for a sixteen-disk backend.

State and persistence behavior: Tests create temporary backend directories and remove them after each object-layer initialization. Config parsing reads YAML files from `testdata/config` but does not persist state. Object-layer initialization may create MinIO metadata on the temporary disks as part of erasure pool setup.

Dependencies and integration points: These tests connect CLI config parsing to erasure layout construction and object-layer initialization. They depend on test helpers from the MinIO cmd package, context cancellation, local filesystem temp roots, and the erasure server-pool implementation.

Risks: The expected pool hash values couple the test to layout hashing details; legitimate config parser or layout changes require fixture/hash updates. The object-layer test asserts a concrete type rather than an interface contract, which is useful for detecting backend selection changes but brittle if implementation names change.

Test signals: Success means valid config files produce two pools with expected hashes, invalid fixtures fail, and both one-disk and sixteen-disk endpoint sets initialize without error as `*erasureServerPools`.
