# sources/user-network-fs/impacket/tests/misc/test_tsts.py

Purpose: Tests Terminal Services Runtime Interface helpers for SID conversion and process-info SID extraction.

Important APIs, types, and functions: Uses `impacket.dcerpc.v5.tsts.binary_sid_to_string`, `RpcWinStationGetAllProcessesResponse`, and `TS_ALL_PROCESSES_INFO`.

Control flow: One test converts a binary SYSTEM SID to canonical SID text. The other constructs a response with one process entry, populates nested pointer data and SID bytes, serializes, reparses, and asserts `getSid()` returns `SYSTEM`.

State and persistence behavior: In-memory NDR structures only.

Dependencies and integration points: Covers TSTS DCE/RPC structure parsing and SID display logic.

Risks: Nested pointer field manipulation is brittle and depends on NDR field internals. SID alias mapping must stay consistent.

Test signals: Good targeted signal for binary SID conversion, populated pointer serialization, response reparse, and friendly SID mapping.
