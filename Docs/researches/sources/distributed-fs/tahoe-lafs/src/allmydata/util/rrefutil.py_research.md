# sources/distributed-fs/tahoe-lafs/src/allmydata/util/rrefutil.py

## Purpose

This module adds version metadata to Foolscap remote references. It probes the remote side for `get_version()` and falls back to a caller-provided default for older peers.

## APIs and control flow

`add_version_to_remote_reference(rref, default)` calls `rref.callRemote("get_version")`. On success it sets `rref.version` to the returned version and returns the reference. On `Violation` or `RemoteException`, interpreted as no usable remote method, it sets `rref.version` to `default` and returns the reference. The function returns the Deferred from the remote call with callbacks attached.

## State, dependencies, risks, and tests

State is mutation of the remote reference object by assigning `.version`. Dependencies are Foolscap `Violation` and `RemoteException`. Integration is with peer negotiation and compatibility paths that need a version field even for old servers.

Risks include treating all `RemoteException` values as absence of `get_version()`, masking remote implementation failures, and callers expecting `.version` before the Deferred fires. Test signals should cover success, missing method via `Violation`, remote exception fallback, unexpected failures not trapped if any, and version field assignment timing.
