# sources/storage-engines/wiredtiger/test/suite/test_prefetch01.py

## Purpose
Validates basic prefetch configuration compatibility between connection-level availability/default settings and session-level enablement.

## APIs, Types, And Functions
Defines `test_prefetch01` with scenarios over `prefetch.available`, `prefetch.default`, and optional session config `prefetch=(enabled=...)`. It uses `helper.copy_wiredtiger_home`, `wiredtiger_open`, `Connection.open_session`, and error pattern matching.

## Control Flow, State, And Persistence
The test copies the current home to a new directory, constructs connection and session configs, and then checks three cases: unavailable plus default-on must fail at connection open, unavailable plus session-enabled must fail at session open, and all other combinations open a session and close cleanly. State is limited to copied home metadata and configuration runtime state.

## Dependencies, Integration, Risks, And Test Signals
Depends on prefetch config parsing and copied-home open semantics. Risks are enabling prefetch when globally unavailable or rejecting valid disabled/default combinations. Signals are expected `pre-fetching cannot be enabled` errors or successful session close.
