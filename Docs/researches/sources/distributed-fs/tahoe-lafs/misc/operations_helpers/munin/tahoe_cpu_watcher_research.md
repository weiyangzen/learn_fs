# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_cpu_watcher

## Purpose

This Munin plugin graphs five-minute CPU averages reported by a CPU watcher JSON endpoint.

## Important APIs, Types, and Functions

It reads endpoint `url` from the environment, parses JSON as `(name, avg1, avg5, avg15)` records, sanitizes Munin field names with `re.sub(r'[^\w]', '_', name)`, and emits config or values.

## Control Flow

The script fetches current data before checking for `config`. It builds config labels for every process and value lines only when `avg5` is not `None`. With `config`, it prints graph metadata and exits; otherwise it prints current values.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence. Dependencies are Munin environment conventions and Python 2 `urllib`. Integration is the CPU watcher service. Risks include network fetch during config calls, field-name collisions after sanitization, no timeout, and JSON shape assumptions. Tests should mock URL data, config/value modes, `None` averages, and colliding process names.
