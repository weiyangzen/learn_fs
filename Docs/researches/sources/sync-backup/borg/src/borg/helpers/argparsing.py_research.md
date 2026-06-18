# sources/sync-backup/borg/src/borg/helpers/argparsing.py

## Purpose
Centralizes Borg's use of `jsonargparse` and flattens nested command namespaces into the single-level namespace expected by command dispatch.

## Important APIs, Types, And Functions
Re-exports `Action`, `ArgumentError`, `ArgumentTypeError`, `RawDescriptionHelpFormatter`, `Namespace`, `ActionSubCommands`, `SUPPRESS`, `REMAINDER`, `register_type`, and `PositiveInt`. `ArgumentParser` subclasses jsonargparse's parser to enforce Borg defaults. `flatten_namespace(ns)` converts nested subcommand namespaces to one `Namespace`.

## Control Flow
The parser hierarchy allows common options at top-level, group-command level, and leaf-command level. `flatten_namespace` walks `subcommand` attributes to build a joined subcommand path, then uses `Namespace.as_flat()` and sorts dotted keys by depth descending so innermost options win. For list values, it merges shallower and deeper lists so append-style options accumulate.

## State And Persistence
No persistent state. The returned `Namespace` is a new object derived from parser output. Parser registrations imported from jsonargparse affect config serialization/deserialization elsewhere.

## Dependencies And Integration Points
Used by archiver parser construction, helper validators, and config-file/environment support from jsonargparse. It is intentionally the only import point for argparse/jsonargparse classes used by Borg.

## Risks And Edge Cases
Precedence depends on dotted-key depth, so unexpected nested keys could collapse to the same destination. List merging assumes outer values should precede inner values. `existing is None` is used as the absence test, so a legitimate `None` from an inner scope does not block outer defaults.

## Test Signals
Tests should include top-level versus subcommand option precedence, two-level subcommands, `SUPPRESS` default behavior, append-list merging, empty subcommand paths, and config/environment values from jsonargparse.
