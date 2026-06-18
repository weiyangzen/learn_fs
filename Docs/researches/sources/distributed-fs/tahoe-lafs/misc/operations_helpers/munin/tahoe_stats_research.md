# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_stats

## Purpose

This generic Munin plugin renders many Tahoe stats/counter graphs from a shared JSON stats file. The specific graph is selected by the plugin executable name or symlink name.

## Important APIs, Types, and Functions

`PLUGINS` maps graph names to a stats key, category (`stats` or `counters`), config header, per-node config template, and value template. `smash_name` sanitizes node names. `open_stats` loads JSON. `main(argv)` selects plugin config, finds the first env var beginning with `statsfile`, filters stale node records with `STAT_VALIDITY = 300`, and emits config or values.

## Control Flow

The basename of `argv[0]` determines the plugin entry. The stats file is loaded once. Config mode prints graph header and per-node labels without age filtering. Normal mode skips nodes whose `timestamp` is older than five minutes and prints values only when the requested stat exists.

## State, Dependencies, Integration, Risks, and Tests

State is the external stats JSON file. Integration is Munin symlinks for runtime load, storage, helper, uploader, and mutable-file metrics. Risks include `plugin_conf` being `None` for unknown names, arbitrary first `statsfile*` env selection, stale filtering based on local clock, field-name collisions, and manual string interpolation. Tests should cover known/unknown plugin names, stale and fresh nodes, missing stat IDs, `.py` basename stripping, and config output.
