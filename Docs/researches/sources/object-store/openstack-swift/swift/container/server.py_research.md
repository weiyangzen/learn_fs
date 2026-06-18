# sources/object-store/openstack-swift/swift/container/server.py

## Purpose

`swift/container/server.py` implements the WSGI container server. It owns the HTTP API used by proxies, object updaters, replication daemons, sharders, and account servers to create containers, update container metadata, record object rows, list objects or shard ranges, delete containers or object rows, and dispatch replication RPCs.

The file bridges request-level protocol details to `ContainerBroker` persistence. It validates placement paths and timestamps, enforces drive and free-space checks, manages container metadata, reports container stats to account servers, redirects object updates to shard containers when possible, and serializes listings in the expected Swift formats.

## Important APIs, Types, and Functions

Module helpers are `gen_resp_headers`, `get_container_name_and_placement`, and `get_obj_name_and_placement`.

`ContainerController(BaseStorageServer)` is the WSGI app. Initialization configures local storage paths, mount/free-space behavior, sync realm validation, allowed sync hosts, replication RPC dispatch, internal account prefixes, optional legacy versions header support, global DB options, a `ContainerSyncStore`, and fallocate reserve settings.

Important methods include `_get_container_broker`, `get_and_validate_policy_index`, `account_update`, `_update_sync_store`, `_redirect_to_shard`, `_update_or_create`, `_should_autocreate`, `_maybe_autocreate`, `_update_metadata`, the public HTTP methods `DELETE`, `PUT`, `HEAD`, `GET`, `REPLICATE`, `UPDATE`, and `POST`, and listing helpers `update_shard_record`, `update_object_record`, `GET_shard`, `GET_object`, and `_create_GET_response`.

`app_factory` and `main` are the paste.deploy and command-line entry points.

## Control Flow

All requests pass through `__call__`. The controller builds a `Request`, stores the transaction id on the logger, rejects invalid internal UTF-8 paths, checks that the method is public, invokes the method, catches `HTTPException` and unexpected errors, and logs a Swift-formatted access line.

Container creation flows through `PUT_container`: the request validates path, timestamp, sync target, drive, and free space; `_update_or_create` initializes or updates the broker while enforcing storage-policy rules; `_update_metadata` persists metadata and resets sync points if the sync target changes; `account_update` sends latest stats to account replicas; the response is `201` or `202` with the policy index.

Object updates flow through `PUT_object` and `DELETE_object`: the object policy is validated or defaulted, `_maybe_autocreate` may create internal containers, `_redirect_to_shard` may return a relative quoted redirect for shard-aware callers, and otherwise the broker records the object put/delete row.

Shard range writes use `PUT_shard`: JSON request body is parsed into `ShardRange` objects, the container may be auto-created when explicitly allowed, metadata is updated, and shard ranges are merged.

Reads flow through `GET`: `X-Backend-Record-Type` plus DB sharding state choose `GET_shard` or `GET_object`. Shard listing supports deleted override, marker/end-marker/includes/reverse, state aliases, namespace vs full format, include-deleted, fill-gaps, and auditing include-own. Object listing selects a storage policy and uses the retiring DB during sharding. `_create_GET_response` serializes XML/JSON/text and returns `204` when empty.

`REPLICATE` validates placement/free space, loads JSON args, and dispatches to `ContainerReplicatorRpc`. `UPDATE` validates and merges proxy-batched object rows. `POST` updates metadata and optionally the put timestamp.

## State and Persistence Behavior

Durable state lives in the container DB at the hashed storage path. The controller persists lifecycle timestamps, storage policy index, metadata, object rows, shard range rows, sync points, and sharding state through `ContainerBroker`.

The controller also mutates the local sync-store symlink tree through `ContainerSyncStore` whenever metadata indicates sync should start or stop, and when containers are deleted.

Account-server state is updated through outgoing `PUT` requests in `account_update`, but failures are logged and later repaired by `container-updater`.

Free-space checks happen before mutating requests and replication RPCs. DB preallocation and query logging flags are configured globally in `swift.common.db`.

## Dependencies and Integration Points

Major dependencies include `ContainerBroker`, `ContainerReplicatorRpc`, `ContainerSyncStore`, request validation helpers, listing format helpers, storage policies, `http_connect`, timestamp and storage utilities, and Swift's swob HTTP classes.

The server is called by proxy servers, object updaters, container replicators, container sharders, sync metadata flows, and account update flows.

## Risks and Edge Cases

Object-update redirection must be opt-in because older object updaters do not understand shard redirects. `_redirect_to_shard` also refuses unsafe unquoted locations unless the caller supports quoted locations, intentionally letting the sharder later move misplaced rows.

Auto-create rules are security and correctness sensitive. Internal accounts may be auto-created, but shard accounts are blocked by default so ordinary updates do not accidentally create shard containers outside the sharder workflow.

Storage policy conflicts are rejected for live containers. Deleted containers may be recreated with a new policy, while object updates retain legacy default policy behavior.

Shard listings have many compatibility paths. Any change can affect proxy listing behavior or sharder audits.

During sharding, object listings read from the retiring DB, so listing semantics depend on broker DB ordering.

Metadata updates reset sync points when sync target changes; missing that reset would skip rows for the new destination.

## Test Signals

High-value tests should exercise response header generation, path validation, policy-index parsing and conflicts, create/recreate/delete flows, metadata and sync-store updates, object PUT/DELETE with auto-create and shard redirect behavior, shard PUT validation, object and shard listings across formats and filters, replication dispatch, UPDATE merge behavior, POST metadata handling, free-space failures, and `__call__` error/logging paths.
