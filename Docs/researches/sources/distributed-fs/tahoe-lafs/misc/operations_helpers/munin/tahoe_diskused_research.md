# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskused

## Purpose

This Munin plugin graphs total disk bytes used across the grid from diskwatcher.

## Important APIs, Types, and Functions

It reads env `url`, loads JSON, and emits the `used` value as `disk_used.value`.

## Control Flow

`config` prints static metadata. Normal mode fetches and prints one value.

## State, Dependencies, Integration, Risks, and Tests

There is no persistent state. Integration is diskwatcher monitoring. Risks are missing env/config, network failures, and schema KeyError. Tests should validate config output and mocked `used` JSON.
