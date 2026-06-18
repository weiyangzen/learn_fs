# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskleft

## Purpose

This Munin plugin graphs total available disk space reported by the diskwatcher web endpoint.

## Important APIs, Types, and Functions

The plugin reads `url` from the environment and expects JSON containing an `available` field.

## Control Flow

If invoked with `config`, it prints static Munin graph metadata and exits. Otherwise it fetches JSON from `url` and prints `disk_left.value`.

## State, Dependencies, Integration, Risks, and Tests

No persistent state is kept. Dependencies are Munin, Python 2 `urllib`, JSON, and the diskwatcher schema. Risks are missing env vars, no network timeout, and KeyError on schema changes. Tests should cover config mode, mocked endpoint data, and missing fields.
