# sources/object-store/minio/cmd/net.go

This file provides networking helpers for startup address validation, local interface discovery, endpoint rendering, host/IP classification, and comparing local addresses. It initializes package-level sets of local IPv4, IPv6, and loopback addresses from network interfaces.

Important functions include `mustSplitHostPort`, `mustGetLocalIPs`, `mustGetLocalIP4`, `mustGetLocalIP6`, `mustGetLocalLoopbacks`, `getHostIP`, `sortIPs`, `getConsoleEndpoints`, `getAPIEndpoints`, `isHostIP`, `extractHostPort`, `isLocalHost`, `sameLocalAddrs`, and `CheckLocalServerAddr`. Endpoint functions honor explicit global endpoint/host settings; otherwise they render URLs for local addresses using TLS state and configured ports. `sortIPs` keeps hostnames first, pushes loopback addresses later, and orders IPv4 addresses by the last octet for friendlier display.

State is computed from OS network interfaces and global MinIO configuration. DNS lookup uses `globalDNSCache.LookupHost(GlobalContext)`. There is no persistence. Integration points include command-line address validation, console/API startup output, endpoint construction, and config errors from `internal/config`.

Risks: package-level address sets are initialized once, so interface changes after startup are not reflected in `localIP4/localIP6/localLoopbacks`. Local-host checks depend on DNS behavior and loopback normalization. `extractHostPort` infers ports from scheme and errors when it cannot. Tests in `net_test.go` cover parsing, sorting, endpoint rendering, local address comparison, and IP detection.
