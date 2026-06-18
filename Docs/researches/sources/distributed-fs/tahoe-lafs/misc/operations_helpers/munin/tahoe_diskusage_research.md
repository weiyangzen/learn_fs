# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_diskusage

## Purpose

This Munin plugin graphs estimated disk usage growth rates across one-hour, one-day, two-week, and four-week windows.

## Important APIs, Types, and Functions

It expects diskwatcher JSON key `rates`, where each item is `(name, timespan, growth, timeleft)`. It maps names to growth bytes per second and emits `rate_1hr`, `rate_1day`, `rate_2wk`, and `rate_4wk` when present.

## Control Flow

Config mode prints static graph metadata with lower-limit settings. Normal mode fetches rates, builds a name-to-growth dict, and conditionally prints available windows.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Dependencies are diskwatcher rate schema and Munin. Risks include silently omitting windows, no timeout, and division/typing assumptions delegated to diskwatcher. Tests should cover partial rate sets, all windows, and malformed tuples.
