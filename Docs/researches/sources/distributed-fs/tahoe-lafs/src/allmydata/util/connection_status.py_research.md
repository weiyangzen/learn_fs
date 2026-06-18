# sources/distributed-fs/tahoe-lafs/src/allmydata/util/connection_status.py

## Purpose

This module converts Foolscap reconnection state into Tahoe's `IConnectionStatus` shape for status displays and diagnostics. It summarizes whether a connection is live, connecting, waiting, or unstarted and preserves per-hint non-connected statuses.

## APIs and control flow

`ConnectionStatus` stores `connected`, `summary`, `non_connected_statuses`, `last_connection_time`, and `last_received_time`. `ConnectionStatus.unstarted()` returns a canonical not-yet-attempted object. `from_foolscap_reconnector()` reads `Reconnector.getReconnectionInfo()`, normalizes byte states, handles `unstarted`, `connected`, `connecting`, and `waiting`, then builds a summary and maps losing hints through `_hint_statuses()`.

## State, dependencies, risks, and tests

State is a snapshot object; there is no persistence. Dependencies are Foolscap `Reconnector`, Tahoe `IConnectionStatus`, zope interfaces, and time injection for waiting summaries.

Risks include assumptions about Foolscap's `ReconnectionInfo` field names, missing `winningHint` in connected state, and fragile human-readable timing for waiting state. Test signals should cover all reconnection states, bytes/native string state values, listener-based connections, multiple hints and handlers, and deterministic waiting text with an injected time function.
