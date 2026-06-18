# sources/object-store/minio/cmd/testdata/config/invalid-types.yaml

Purpose: negative YAML fixture for endpoint type homogeneity. It mixes a local filesystem endpoint (`/mnt/disk{1...4}/`) into an otherwise HTTPS distributed pool.

Important structure: all top-level config fields and options match the valid examples, but the first endpoint in the first pool lacks an HTTP/S scheme while the remaining endpoints are HTTPS URLs.

Control flow and integration: parser tests should accept the YAML syntax, then reject the endpoint set during endpoint-type validation. Distributed pools must not mix local path endpoints and remote URL endpoints in this shape.

State and persistence: static fixture only; successful parsing should not persist or initialize this topology.

Dependencies: depends on endpoint type detection (`path` versus URL endpoint) and pool validation code.

Risks: accepting mixed endpoint types can lead to ambiguous local/remote disk ownership and broken erasure setup. The fixture protects the validation boundary from regressions.

Test signals: expected failure is a semantic endpoint-type validation error, distinct from malformed YAML or disk-count mismatch.
