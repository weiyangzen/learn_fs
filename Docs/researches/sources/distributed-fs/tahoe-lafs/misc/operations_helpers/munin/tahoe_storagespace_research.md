# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_storagespace

## Purpose

This Munin plugin reports disk bytes consumed by each configured Tahoe node's `storage` directory.

## Important APIs, Types, and Functions

It discovers env vars named `basedir_NODE`, builds config fields, and runs `du --bytes --summarize <basedir>/storage` through Python 2 `commands.getstatusoutput`.

## Control Flow

Config mode emits one series per node. Normal mode runs `du` for each node, exits with `du`'s return code on failure, parses the byte count, and prints `<node>.value`.

## State, Dependencies, Integration, Risks, and Tests

State is local filesystem measurement. Dependencies are GNU `du --bytes`, Python 2 `commands`, and Munin. Risks include shell injection or breakage from unquoted paths in the command string, portability issues on non-GNU systems, expensive scans, and unsanitized node names. Tests should mock command output, paths with spaces/shell metacharacters, and nonzero return codes.
