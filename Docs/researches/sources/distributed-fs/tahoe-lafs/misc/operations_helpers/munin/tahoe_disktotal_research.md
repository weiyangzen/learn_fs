# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_disktotal

## Purpose

This Munin plugin graphs total and used disk capacity across the grid from diskwatcher JSON.

## Important APIs, Types, and Functions

It reads `url`, expects JSON keys `total` and `used`, and emits Munin fields `disk_total` and `disk_used`.

## Control Flow

`config` mode prints graph title, vlabel, category, and field draw styles. Normal mode fetches the endpoint and prints both values.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration is diskwatcher-to-Munin monitoring. Risks include endpoint failure causing plugin failure, no validation of numeric values, and Python 2 dependencies. Tests should mock JSON responses for config and normal paths.
