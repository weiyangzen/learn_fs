# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_connection_status.py

## Purpose
This file tests conversion from Foolscap reconnection information to Tahoe's user-facing connection status model. It validates summary strings, connected flags, non-connected hint statuses, and timestamps.

## Important APIs, Types, And Functions
Helpers are `reconnector`, `connection_info`, and `reconnection_info`, which construct Foolscap `Reconnector`, `ConnectionInfo`, and `ReconnectionInfo` objects with test data. `Status` tests `connection_status._hint_statuses` and `connection_status.from_foolscap_reconnector`.

## Control Flow
Each test builds a synthetic reconnection state and passes it to the conversion function. Connected tests cover a winning hint and listener-based connections. Non-connected tests cover `connecting` and `waiting`, including injected `time=lambda: 12` to make the retry summary deterministic.

## State, Persistence, And Dependencies
There is no persistence. The tests reach into private Foolscap attributes like `_reconnectionInfo`, so they are coupled to Foolscap internals.

## Risks And Test Signals
The file guards status text that appears in diagnostics and UIs. It catches errors in hint/handler labeling, hiding non-winning connector statuses, and elapsed/retry time formatting.
