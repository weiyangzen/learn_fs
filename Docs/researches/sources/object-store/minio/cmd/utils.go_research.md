# sources/object-store/minio/cmd/utils.go

Broad command-layer utility file. It normalizes backend errors (`ErrorRespToObjectError`), parses bucket/object paths, wraps request bodies with checksum verifiers, defines S3 object/part limits, manages profiler start/stop/data collection, creates HTTP/TLS transports, builds request/audit context, formats dumped requests, encodes directory marker objects, supports OpenID test login, filters Veeam storage classes, and provides generic helpers such as sorted map keys.

State interactions include temporary profiler files, runtime profiler rates, global profiler registry, global DNS/root CA/TCP config, IAM config reads, audit logging, request info mutation, and Veeam env-controlled behavior. Dependencies span MinIO internals, `madmin`, `minio-go`, OIDC/OAuth2, pprof/trace, fgprof, HTTP/TLS, and logger/audit packages.

Risks are high because many hot paths depend on this file: error mapping omissions, checksum body semantics, global profiler toggles, TLS posture, and request context correctness. `utils_test.go` covers several boundary helpers, but transports, checksum wrapping, audit, OpenID flow, Veeam filtering, and many error mappings are not directly tested here.
