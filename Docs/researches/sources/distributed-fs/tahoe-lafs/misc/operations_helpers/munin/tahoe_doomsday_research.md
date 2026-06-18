# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_doomsday

## Purpose

This Munin plugin graphs estimated days remaining before storage exhaustion, using diskwatcher growth-rate projections.

## Important APIs, Types, and Functions

It reads `rates` from JSON and maps each rate name to `timeleft` seconds when nonzero. It converts seconds to days with `DAY = 24*60*60`.

## Control Flow

Config mode prints four days-left series. Normal mode fetches rates, filters falsy `timeleft`, and emits present windows divided by `DAY`.

## State, Dependencies, Integration, Risks, and Tests

No state is persisted. Integration is capacity planning in Munin. Risks include omitting zero/None projections, no timeout, Python 2 integer division depending on value types, and stale assumptions about rate names. Tests should cover zero, None, and positive timeleft values.
