# sources/object-store/openstack-swift/swift/cli/manage_shard_ranges.py

Purpose: operator tool for finding, installing, enabling, compacting, repairing, and analyzing container shard ranges by directly modifying one container database replica.

Important APIs: command functions `find_ranges()`, `show_shard_ranges()`, `db_info()`, `delete_shard_ranges()`, `merge_shard_ranges()`, `replace_shard_ranges()`, `find_replace_shard_ranges()`, `enable_sharding()`, `compact_shard_ranges()`, `repair_shard_ranges()`, `analyze_shard_ranges()`, parser builder `_make_parser()`, and `main()`. Exceptions distinguish gaps, invalid state, and invalid repair solutions.

Control flow: `main()` parses a subcommand, loads optional container-sharder config for default values, validates config, and either analyzes JSON input or opens a `ContainerBroker`. Find scans broker rows into shard data. Replace validates contiguous ranges against the broker own shard range, deletes existing ranges, merges new ranges, and optionally enables sharding. Enable updates the own shard range to SHARDING, stamps epoch, updates stats, and writes `X-Container-Sysmeta-Sharding`. Compact finds small shard sequences and marks donors/acceptors for sharder processing. Repair either expands active neighbors into gaps or chooses a complete acceptor path and finalizes overlapping donors as shrinking.

State and persistence: directly mutates container DB shard-range rows, own shard range, metadata, deleted flags, timestamps, and compaction/repair states. It may commit pending updates unless `--skip-commits` is used.

Dependencies and integration: deeply integrated with `ContainerBroker`, `ShardRange`, `ShardRangeList`, `CleavingContext`, and container sharder algorithms/config. Replicator and sharder daemons consume the DB changes later.

Risks: high blast radius; docs warn to run on one replica. Deleting or replacing ranges after enabling sharding can make replicas inconsistent. Repair intentionally rejects sharding/shrinking states and young overlaps to avoid transient false positives. Operator prompts are bypassed by `--yes` and dry-run prevents writes.

Test signals: parser/default config coverage, JSON validation, contiguous range checks, timeout contexts, enable idempotence, compaction selection, gap repair, overlap repair rejection paths, dry-run/yes prompts, invalid DB handling, and analyze-only behavior.
