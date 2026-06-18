# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_fetched

## Purpose

This Munin plugin graphs bytes fetched by the Tahoe CHK upload helper.

## Important APIs, Types, and Functions

It fetches JSON from env `url` and emits `chk_upload_helper.fetched_bytes` as a GAUGE field named `fetched`.

## Control Flow

Config mode prints static metadata including min zero. Normal mode prints the fetched byte value.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration is upload-helper Munin monitoring. Risks include treating what may be a counter as a gauge, endpoint failures, and Python 2 urllib reliance. Tests should mock stats JSON and verify both modes.
