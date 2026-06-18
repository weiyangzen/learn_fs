# sources/object-store/openstack-swift/swift/cli/ringbuilder.py

## Purpose
`ringbuilder.py` implements the `swift-ring-builder` CLI for creating, inspecting, modifying, rebalancing, validating, and serializing Swift ring builder files and distributable ring files. It is the primary operator interface for account, container, object, and composite-adjacent ring lifecycle work, including partition-power increase coordination for object rings.

## Important APIs, types, and functions
- Global version/exit constants define CLI status behavior: success 0, warning 1, error 2.
- `format_device()` produces stable human-readable device descriptions with IPv6 bracket handling.
- Parser helpers (`_parse_search_values`, `_parse_list_parts_values`, `_parse_add_values`, `_parse_set_*_values`, `_parse_remove_values`) normalize old-style device strings and new option-style inputs.
- `check_devs()` guards multi-device destructive changes with interactive confirmation unless `--yes` is supplied.
- `_set_weight_values()`, `_set_region_values()`, `_set_zone_values()`, and `_set_info_values()` mutate device dictionaries through `RingBuilder` APIs or direct metadata updates after duplicate checks.
- `_make_display_device_table()` builds aligned device table printers for default output.
- `Commands` is a static-method command table for `create`, default display, `version`, `search`, `list_parts`, `add`, `set_weight`, `set_region`, `set_zone`, `set_info`, `remove`, `rebalance`, `dispersion`, `validate`, `write_ring`, `write_builder`, `pretend_min_part_hours_passed`, `set_min_part_hours`, `set_replicas`, `set_overload`, and partition-power commands.
- `main(arguments=None)` maps ring/builder filenames, loads builders, creates backups dir, optionally locks the parent directory for `-safe` invocations, and dispatches commands.
- `error_handling_main()` installs an excepthook so uncaught exceptions print a traceback and exit with status 2.

## Control flow
Startup parses the builder/ring filename pair with `parse_builder_ring_filename_args`, loads a `RingBuilder` except for `create`, `write_builder`, or `version`, and warns if a ring file path was translated to a builder path. It creates a sibling `backups` directory. With no command it displays global ring state, ring-file freshness, device balance table, and partition-power progress instructions.

Device commands parse search or add syntax through `swift.common.ring.utils`, confirm broad matches, mutate the builder, and save the builder file. Adds and removes are blocked while partition-power increase is in progress. `set_info` directly changes IP/port/device/meta fields after checking no other device already uses the target endpoint/device tuple; it does not itself require rebalance, though `write_ring` may be needed.

`rebalance` parses force, seed, debug, and ring format options. It refuses to run while partition-power increase is active, captures pre-rebalance balance/dispersion, calls `builder.rebalance()`, handles min-part-hours and empty-ring errors, rejects low-impact saves unless forced or device metadata changed, validates the result, prints balance/dispersion warnings, then saves timestamped backups plus current `.ring.gz` and builder files. `write_ring` serializes current ring data without a rebalance and warns when writing a ring with devices but no assignments. `write_builder` reconstructs a lossy builder from a ring file.

Partition-power commands enforce object-ring-only preparation, transition `next_part_power` through prepare, increase, cancel, and finish states, and print explicit operational instructions to run `swift-object-relinker` between ring deployment steps. `dispersion` can recalculate and save cached dispersion data, prints graph rows, and exits warning when placement is imperfect.

## State and persistence behavior
The command mutates builder files, distributable ring files, and backup files under `backups/`. `rebalance` and `write_ring` write ring data with a selected serialization format. Device changes update persistent device dictionaries and builder version state. `write_builder` can create a new builder from existing ring data, but loses some original builder metadata such as exact min-part-hours unless supplied. Safe-mode invocations lock the builder parent directory for 15 seconds to avoid concurrent writes.

## Dependencies and integration points
The CLI is a thin but broad integration layer over `RingBuilder`, `Ring`, `RingData`, `CompositeRingBuilder` detection, ring serialization codecs, ring utility parsers, dispersion reporting, validation exceptions, parent-directory locks, and IPv6 validation. Operators use its outputs and exit codes in ring deployment automation. Its partition-power commands are coupled to `swift-object-relinker` and object server rollout order.

## Risks and edge cases
The module relies on global `argv`, `builder`, `builder_file`, `ring_file`, and `backup_dir`, making command methods hard to compose and sensitive to tests that do not reset globals. Many helpers call `exit()` directly, so library-style callers cannot recover cleanly. Interactive confirmation can block automation unless `--yes` is used. Direct device-dict mutation in `set_info` must stay compatible with builder invariants. Rebalance save refusal is intentionally conservative and may surprise users after small improvements. Partition-power commands can affect data availability if rings are deployed before relink/cleanup steps complete.

## Test signals
Important tests should cover both old and new command syntax, IPv6 formatting, duplicate device detection, interactive abort and `--yes`, empty and invalid builder handling, rebalance warning/error/save thresholds, ring format option behavior, backup creation, safe-mode locking, partition-power command sequencing, lossy `write_builder`, and exception-to-exit-code mapping in `error_handling_main()`.
