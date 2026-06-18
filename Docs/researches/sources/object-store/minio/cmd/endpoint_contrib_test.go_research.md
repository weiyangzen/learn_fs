# sources/object-store/minio/cmd/endpoint_contrib_test.go

Purpose: Contributed test coverage for endpoint-domain IP derivation. It verifies that `updateDomainIPs` records only non-loopback, non-localhost addresses with the correct port normalization.

Important APIs/types/functions: `TestUpdateDomainIPs` saves/restores `globalMinioPort` and `globalDomainIPs`, then feeds `set.StringSet` endpoint inputs into `updateDomainIPs`. Cases cover empty input, localhost-only input, hostnames/IPs without ports, and mixed explicit/default ports.

Control flow and state: The test mutates global endpoint-related variables in a scoped manner. Each case resets `globalDomainIPs`, calls the production helper, and compares the resulting set to the expected set.

Dependencies and integration points: Depends on `github.com/minio/minio-go/v7/pkg/set` and the `endpoint.go` helper. It is an integration signal for cluster bootstrap because `globalDomainIPs` is later used for domain/IP awareness.

Risks: The test uses literal private IPv4 values and does not exercise DNS hostnames, IPv6, or failure paths from `getHostIP`. It is sensitive to global-state cleanup, which it handles with defers.

Test signals: Strongly validates default port behavior and loopback filtering for IPv4-style endpoint inputs.
