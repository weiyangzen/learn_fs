# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_helperstats_active

## Purpose

This Munin plugin graphs the number of active upload-helper files.

## Important APIs, Types, and Functions

It reads JSON from env `url` and emits `chk_upload_helper.active_uploads` as `fetched.value`; the field name is historically `fetched` despite representing active files.

## Control Flow

Config mode prints graph metadata. Normal mode fetches JSON and prints the active upload count.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Integration is Tahoe upload-helper statistics monitoring. Risks include misleading graph vlabel/field name, no timeout, and KeyError on stats changes. Tests should cover config output and JSON fixtures.
