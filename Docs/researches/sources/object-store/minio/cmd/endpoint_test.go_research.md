# sources/object-store/minio/cmd/endpoint_test.go

Purpose: Unit and topology tests for endpoint parsing, endpoint-list validation, pool endpoint creation, and peer discovery. These tests encode the expected behavior for local erasure versus distributed erasure setup selection.

Important APIs/types/functions: `TestNewEndpoint` validates path and URL parsing plus error messages for empty roots, bad schemes, bad query fragments, invalid ports, empty hosts, root URL paths, and IP-without-scheme input. `TestNewEndpoints` checks duplicate detection and mixed style/scheme rejection. `TestCreateEndpoints` drives `mergeDisksLayoutFromArgs` and `CreatePoolEndpoints` through single-drive path setup, URL-only local setups, distributed setups, path conflicts, same-host different-port conflicts, and local host naming conflicts. `TestGetLocalPeer` and `TestGetRemotePeers` validate peer selection.

Control flow and state: Tests temporarily set `globalMinioPort`, use local non-loopback IP discovery, build expected `url.URL` values, and compare endpoint strings/setup types. The tests run through real endpoint normalization and locality detection paths rather than stubbing all network behavior.

Dependencies and integration points: Integrates with server context layout parsing, setup type constants, `mustGetPoolEndpoints`, local IP discovery, and endpoint peer APIs from `endpoint.go`. It also exercises config-error wrapping through expected error strings.

Risks: Tests may skip or fail on hosts without a non-loopback IPv4 address. Because locality resolution depends on host/network behavior, assertions around local flags are tied to the test environment. The tests mostly compare strings and setup types, not every index field.

Test signals: Provides broad regression coverage for endpoint bootstrap rules, especially error text and topology invariants that operators see during startup.
