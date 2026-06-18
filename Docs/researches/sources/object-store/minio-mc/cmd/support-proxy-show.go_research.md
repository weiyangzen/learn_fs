<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-show.go -->
# sources/object-store/minio-mc/cmd/support-proxy-show.go

Purpose: implements `mc support proxy show TARGET`, retrieving the configured SUBNET proxy from MinIO.

Important APIs/types/functions: `supportProxyShowCmd`, `supportProxyShowMessage`, `checkSupportProxyShowSyntax`, and `mainSupportProxyShow`.

Control flow: validates one argument, sets success color, extracts alias, requires registration, calls `getKeyFromSubnetConfig(alias, "proxy")`, errors when the server does not support proxy configuration, and prints either the proxy value or "Proxy is not configured".

State and persistence: read-only; no local or remote mutation.

Dependencies and integration points: part of the support proxy command group; depends on MinIO config access through shared `getKeyFromSubnetConfig` and global JSON/text output.

Risks and test signals: output semantics distinguish unsupported config from supported-but-empty config. Tests should cover both cases, JSON status fields, missing argument handling, and registration failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-show.go -->
