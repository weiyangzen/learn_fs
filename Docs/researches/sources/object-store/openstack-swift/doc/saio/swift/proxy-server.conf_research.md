# sources/object-store/openstack-swift/doc/saio/swift/proxy-server.conf

## Purpose
SAIO public proxy-server config. It exposes Swift at `127.0.0.1:8080` with a feature-rich middleware chain used by local development and probe tests.

## Important Sections
The pipeline includes `catch_errors`, `gatekeeper`, `healthcheck`, two `proxy-logging` passes, `cache`, `etag-quoter`, `listing_formats`, `bulk`, `tempurl`, `ratelimit`, `crossdomain`, `container_sync`, `tempauth`, `staticweb`, copy/quota/SLO/DLO/versioned-writes/symlink/keymaster/encryption middleware, and `proxy-server`. Tempauth defines admin/test users. Container sync points to realm `//saio/saio_endpoint`. Versioned writes and object versioning are enabled. S3API is defined but commented as opt-in by pipeline placement.

## Control Flow and Integration
PasteDeploy applies middleware in the listed order. Public and internal client requests pass through authentication, formatting, large-object handling, versioning, symlink, encryption, and logging before the proxy app routes to rings. The duplicate proxy logging captures middleware-originated requests.

## State and Persistence Behavior
The proxy itself persists little local state; it routes to account/container/object servers and uses memcache. Middleware changes Swift cluster state: versioned writes, quotas, SLO/DLO manifests, tempurl auth, container sync, symlink targets, and encryption metadata.

## Risks and Test Signals
This is intentionally broad for SAIO; production would need real auth, secrets, TLS, and tuned middleware. Placeholder encryption secret and tempauth users are unsafe outside development. Test signals include successful proxy startup, auth with configured users, versioned-write behavior, encrypted object handling, and probe coverage across middleware.
