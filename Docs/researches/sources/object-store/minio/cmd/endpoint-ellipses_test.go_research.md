<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint-ellipses_test.go -->
## sources/object-store/minio/cmd/endpoint-ellipses_test.go

Purpose: This file validates endpoint ellipses parsing, erasure set-size selection, endpoint-server creation, and special expansion cases for MinIO server startup arguments.

Important APIs and functions: `TestCreateServerEndpoints` tests `mergeDisksLayoutFromArgs` plus `createServerEndpoints`. `TestGetDivisibleSize` tests GCD behavior. `TestGetSetIndexesEnvOverride` and `TestGetSetIndexes` test `getSetIndexes`. Helpers `getHexSequences` and `getSequences` build expected sequences. `TestParseEndpointSet` tests `parseEndpointSet` and expected `endpointSet` structures.

Control flow: Creation tests cover invalid empty args, malformed ranges, duplicate disks, localhost port conflicts, and valid filesystem/distributed/ellipses inputs. Set-index tests construct `ellipses.ArgPattern` values from args and assert either exact set index arrays or expected failure. Override tests pass explicit set-drive counts to verify accepted and rejected manual choices. Parse tests compare full `endpointSet` values including pattern prefixes, suffixes, generated sequences, and computed set indexes for numeric, padded numeric, multi-dimensional, Kubernetes-style, standalone, multi-ellipses, and IPv6 hexadecimal cases.

State and persistence behavior: Tests operate in memory and mutate only temporary `serverCtxt` values. No persisted layout files are written. The expected `cmdline` behavior for config-file hashing is not covered in this listed test file.

Dependencies and integration points: The file depends on `reflect`, `testing`, `fmt`, and `github.com/minio/pkg/v3/ellipses`. It exercises startup layout code and, through `createServerEndpoints`, endpoint validation functions elsewhere in the package.

Risks: Many assertions use exact deeply nested slices; this is good for regression detection but means intentional layout-selection changes require broad fixture updates. Tests cover many expansion forms but not config-file list expansion, uneven per-node config-file disk counts, mixed local/distributed config-file pools, or duplicate detection performance on huge expansions. Environment parsing itself is not exercised through the real environment variable in the override tests; they pass the override value directly into `getSetIndexes`.

Test signals: The file provides strong coverage for the core endpoint expansion and set sizing algorithms, including failure paths and real-world distributed patterns.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint-ellipses_test.go -->
