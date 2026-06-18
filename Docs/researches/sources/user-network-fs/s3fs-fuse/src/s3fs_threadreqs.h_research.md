# sources/user-network-fs/s3fs-fuse/src/s3fs_threadreqs.h

Purpose: declares request parameter structs, worker entry points, high-level request wrappers, multipart helpers, and direct IAM request helpers for s3fs-fuse's threaded request layer.

Important APIs and types: structs such as `head_req_thparam`, `multi_head_req_thparam`, `multipart_upload_part_req_thparam`, `multipart_put_head_req_thparam`, and `parallel_get_object_req_thparam` define the data shared between caller and worker. Public functions include synchronous wrappers for HEAD/DELETE/PUT/list/check/get, asynchronous multi-head and multipart/parallel operations, and direct IAM token/role/credential calls. `retrycnt_t` maps paths to retry counts.

Control flow: headers expose a two-level API: worker functions compatible with `ThreadPoolMan`, and utility wrappers that callers should use. Some wrappers are await-style and stack-safe; others require heap-allocated params because workers outlive the scheduling call.

State and persistence: structs hold pointers to caller-owned state (`headers_t`, locks, semaphores, result ints, ETag records, response strings). Correct lifetime is part of the API contract. No global state is declared here.

Dependencies and integration points: includes metadata headers, curl, fdcache page data, object lists, sync filler, and semaphores. Used by filesystem operation code and by credential metadata refresh code.

Risks: many raw pointers are nullable in structs and validated only at runtime. Callers must keep pointed-to locks/results/ETags/semaphores alive until workers finish. Function signatures expose low-level file descriptors and offsets, so invalid descriptors/ranges propagate to network/file I/O paths.

Test signals: compile-time coverage for all declarations, lifecycle tests around async wrappers, null-parameter worker tests, and integration tests using fake `ThreadPoolMan`/`S3fsCurl` to verify parameter propagation.
