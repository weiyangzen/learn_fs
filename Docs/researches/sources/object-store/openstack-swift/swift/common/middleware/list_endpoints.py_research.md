# sources/object-store/openstack-swift/swift/common/middleware/list_endpoints.py

Purpose: WSGI middleware exposing an unauthenticated `/endpoints/` REST API that maps a Swift account, container, or object to the internal storage-node endpoint URLs that would serve it. It is intended for trusted in-cluster clients such as Hadoop locality integrations.

Important APIs and control flow: `ListEndpointsMiddleware` loads account and container rings at construction, lazily gets object rings with `POLICIES.get_object_ring`, parses optional `v1` or `v2` response versions, and rejects non-GET requests with `HTTPMethodNotAllowed`. `__call__` unquotes account/container/object names, queries the appropriate ring, builds `http://ip:port/device/partition/...` endpoints, and formats v1 as a JSON list or v2 as a JSON object with backend headers. Object lookups call `get_container_info(..., swift_source='LE')` to discover the storage policy before choosing the object ring.

State, dependencies, and integration: Persistent state is ring files under `swift_dir`; request-time state is only local variables. It integrates with Swift rings, storage policies, and proxy controller container-info lookups.

Risks and test signals: The module deliberately bypasses auth, so pipeline placement and network exposure are critical. Tests should cover version parsing, default version fallback, invalid versions, percent-encoding, object policy headers, custom endpoint paths, non-GET rejection, and account/container/object ring selection.
