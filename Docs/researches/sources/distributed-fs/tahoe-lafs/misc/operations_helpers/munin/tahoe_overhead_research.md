# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_overhead

## Purpose

This Munin plugin estimates Tahoe storage overhead by comparing actual disk usage with ideal encoded deep size and inactive-account size metrics.

## Important APIs, Types, and Functions

It reads `diskwatcher_url` for JSON `used` and `deepsize_url` for JSON keys `all` and `active`. It assumes `k=3`, `N=10`, computes ideal expansion, overhead percentage, effective expansion, and inactive savings.

## Control Flow

Config mode prints overhead, inactive, and hidden effective-expansion fields. Normal mode fetches both endpoints, prints overhead and effective expansion only if overhead is positive, and always prints inactive savings.

## State, Dependencies, Integration, Risks, and Tests

No persistence. Integration is capacity/garbage monitoring. Risks include hard-coded 3-of-10, division by zero for empty active/all values, suppressing negative overhead, no timeout, and external PHP/deepsize dependency. Tests should cover positive/negative overhead, inactive calculations, and zero deep-size guards.
