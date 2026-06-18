# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_nodememory

## Purpose

This Munin plugin reads Tahoe node `twistd.pid` files and graphs process memory from `/proc/<pid>/status`.

## Important APIs, Types, and Functions

It discovers nodes from env vars named `nodememory_NODE`, reads `twistd.pid`, extracts `VmSize` and `VmRSS`, and emits byte values by multiplying reported kB by 1024.

## Control Flow

After collecting pids, config mode prints one series per node/field. Normal mode reads `/proc` status for live pids and prints available field values.

## State, Dependencies, Integration, Risks, and Tests

State is local procfs and pid files. Integration is Linux Munin monitoring. Risks include Python 3 failure from `list.sort(lambda...)`, stale pids, permission/read races, unsanitized node names, and Linux-only `/proc` assumptions. Tests should use temporary pid files with mocked `/proc` paths or refactorable reader fixtures, including vanished pids.
