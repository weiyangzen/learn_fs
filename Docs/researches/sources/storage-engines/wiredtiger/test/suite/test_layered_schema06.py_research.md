# sources/storage-engines/wiredtiger/test/suite/test_layered_schema06.py

## Purpose

This suite validates WiredTiger file ID namespaces for disaggregated layered metadata. It ensures special shared files have fixed IDs, local and shared dynamic files use the correct namespaces, prohibited PALI-reserved IDs are not emitted, and leader/follower metadata remains consistent.

## Important APIs, Types, and Functions

Constants model local, shared, and special namespaces and the three namespace bits. `extract_id` from `metadata_helper` parses file IDs from metadata values. `check_metadata_ids` iterates `metadata:` entries, validates fixed IDs for `WiredTigerShared.wt_stable`, `WiredTigerSharedHS.wt_stable`, and `metadata:`, validates dynamic namespaces for `WiredTigerHS.wt` and explicit layered stable/ingest files, and fails on unexpected file/metadata entries.

## Control Flow

Tests cover an empty leader and follower, one table populated on the leader, one table picked up by a follower after checkpoint transfer, ten tables picked up by a follower, and ten tables created on both leader and follower. Creation formats include bare layered, layered with disagg block manager, and `table:` layered type. Expected stable files are shared namespace; ingest files are local namespace.

## State, Persistence, and Dependencies

State lives in metadata IDs assigned by schema creation, implicit history store creation, shared metadata, and checkpoint pickup. Dependencies include `re`, `wttest`, `metadata_helper`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

Risks include backward-incompatible fixed ID changes, namespace collisions, use of PALI-reserved IDs, duplicate IDs in a namespace, follower ingest files receiving shared IDs, and unexpected metadata entries. The signal is comprehensive metadata iteration with explicit expected-file maps for each scenario.
