<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-set.go -->
# sources/object-store/minio-mc/cmd/support-proxy-set.go

Purpose: implements `mc support proxy set TARGET PROXY_URL`, storing a SUBNET proxy URL in MinIO server config.

Important APIs/types/functions: `supportProxySetCmd`, `supportProxySetMessage`, `checkSupportProxySetSyntax`, and `mainSupportProxySet`.

Control flow: after two-argument validation and registration enforcement, it builds an admin client, rejects an empty proxy string, parses the URL with `net/url.Parse`, writes `subnet proxy=<proxy>` via `SetConfigKV`, and prints a success message.

State and persistence: persists the proxy setting in remote MinIO server config. No local files are modified.

Dependencies and integration points: integrated under `support proxy`; depends on shared output/color helpers, `url2Alias`, `getClient`, and admin config APIs.

Risks and test signals: `url.Parse` alone accepts some strings without scheme/host, so validation may be looser than expected. Tests should cover empty proxy, malformed or scheme-less strings, config write errors, JSON output, and registration requirements.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-set.go -->
