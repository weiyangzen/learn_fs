# sources/user-network-fs/nfs-ganesha/src/tools/ganesha-rados-grace.c

Purpose: administrative CLI for inspecting and mutating the RADOS-backed grace-period database used for coordinated NFS grace handling.

Important APIs, types, and functions: `cluster_connect` creates a librados client, reads config, connects, optionally creates the pool, creates an ioctx, and sets namespace. `main` parses long options and dispatches commands to `rados_grace_dump`, `rados_grace_create`, `rados_grace_add`, `rados_grace_join_bulk`, `rados_grace_lift_bulk`, `rados_grace_enforcing_toggle`, and `rados_grace_member_bulk`.

Control flow: defaults to `dump`, with defaults for pool and oid from `rados_grace.h`. Node arguments are normalized: numeric node ids get a `node` prefix, non-numeric names are used as-is. `add` creates the pool/object if needed, then adds members. Other commands require at least one node except `dump`.

State and persistence: mutates persistent Ceph RADOS pool/object state. Local process state includes allocated node name strings and a RADOS ioctx; cleanup is minimal at process exit.

Dependencies and integration points: depends on librados, Ceph configuration, and the project's `rados_grace` support library. It is an operator-facing companion to server grace coordination.

Risks: `cluster_connect` returns early without destroying partially created RADOS handles on failure. `node_names` is not initialized when no nodes are supplied, though it is only used in node command paths. Allocation length for node names omits an explicit extra byte in the non-numeric case but uses `calloc(1, len)` and `snprintf(..., len, ...)`, truncating the final character if `len == strlen(arg)`. RADOS mutations are direct and should be used carefully.

Test signals: requires integration tests against a test Ceph cluster or mocked librados/rados_grace layer. CLI parsing can be unit-tested for node normalization and command dispatch.
