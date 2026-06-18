# sources/storage-engines/foundationdb/contrib/metadata_audit/check_krm_corruption.py

## Purpose
`check_krm_corruption.py` is an operational diagnostic and repair utility for FoundationDB metadata corruption around `keyServers`, `serverKeys`, and `serverList` system keyspaces. It is focused on failure modes that can leave Data Distribution or storage servers stuck: uncoalesced KeyRangeMap entries, stale/dead server references, `keyServers`/`serverKeys` ownership disagreement, storage servers missing shards they are supposed to own, orphaned `serverKeys`, and mismatches between metadata and currently running storage roles.

The script is designed to be run from a FoundationDB cluster operator environment. It can run read-only scans, call `fdbcli status json`, integrate JSON from the C++ `audit_ss_shards` tool, probe ranges with Python client reads or metrics calls, and, behind explicit flags plus confirmation, delete selected stale metadata.

## Important APIs, Types, And Functions
The file is a flat Python CLI module. It imports the local vendored `fdb` binding plus metadata constants and lock helpers from `fdb_metadata_utils`: `KEY_SERVERS_PREFIX`, `SERVER_KEYS_PREFIX`, `SERVER_LIST_PREFIX`, matching end keys, `strinc`, transaction option helper, and MoveKeys lock functions.

Binary encoding helpers include `decode_compressed_int`, `encode_compressed_int`, `decode_key_servers_value`, `decode_key_servers_value_simple`, and `encode_key_servers_value`. They understand both old compressed-int `keyServers` values and versioned FDB 6.2+ / 7.2+ values with protocol versions, source/destination server UID vectors, and optional shard IDs. Constants such as `FDB_PROTOCOL_VERSION_62`, `FDB_PROTOCOL_VERSION_72`, `FDB_PROTOCOL_VERSION_73`, and `ANONYMOUS_SHARD_ID` drive re-encoding.

Diagnostics for raw values and round-trip safety are handled by `hex_dump`, `analyze_keyservers_value_format`, `test_keyservers_encoding_roundtrip`, and `test_serverkeys_encoding_roundtrip`. Server identity and status conversion helpers include `status_id_to_serverlist_prefix`, `serverlist_uid_to_status_format`, `uid_cpp_to_raw`, and `uid_raw_to_cpp`, reflecting the different byte orders used by `serverList`, status JSON, and C++ `UID::toString()`.

Metadata readers and analyzers include `get_server_list`, `check_serverlist_vs_running`, `extract_storage_servers_from_status`, `get_cluster_status`, `check_key_servers`, `check_server_keys`, `check_keyservers_serverkeys_mismatch`, `check_wrong_shard_server`, `build_serverkeys_map_for_servers`, `get_serverkeys_ranges_for_orphan_servers`, `compare_server_sets`, and `attempt_server_id_mapping`.

Audit integration is centered on `run_audit_ss_shards`, `load_audit_json`, `is_keyservers_audit`, `generate_audit_comparison_report`, `process_keyservers_audit`, `correlate_audit_with_metadata`, `correlate_stale_serverkeys_with_keyservers`, and `three_way_metadata_correlation`. Repair entrypoints are `repair_serverkeys_from_audit`, `repair_keyservers_from_audit`, and `repair_keyservers_phantom_shards`, with `main()` wiring all CLI modes.

## Control Flow
Startup parses many flags in `main()`. If `--report-audit` is supplied, audit JSON is loaded first and later folded into the full diagnostic run. If `--repair-from-audit` is supplied, the script validates that the requested repair matches the audit mode, opens the database, chooses dry-run unless `--execute-repair` is present, optionally takes the MoveKeys lock, invokes the selected repair routine, releases the lock, and exits.

The standalone `--range-probe-keyservers` mode opens FDB, scans `keyServers` into ranges, separates user ranges from `\xff` system ranges, probes user ranges with `verify_ranges_with_get_range`, and exits.

The default path opens FDB, prints read-only mode, gets cluster status through `fdbcli`, and optionally runs `check_serverlist_vs_running`. It then executes `run_checks` as an `@fdb.transactional` function with read-system-keys and lock-aware options. `run_checks` reads `serverList`, scans `keyServers`, scans `serverKeys`, counts blog keyspace entries, reports KRM and server-reference findings, optionally samples `keyServers`/`serverKeys` mismatches, and by default runs the full `wrong_shard_server` metadata check.

After the transactional checks, `main()` compares server sets against running status data, can run encoding round-trip tests, analyzes orphan servers, attempts storage-server discovery through special keys and address mapping, optionally probes all `keyServers` ranges with point reads, integrates preloaded or freshly executed C++ audit output, performs audit/metadata correlations, and prints an executive DD-impact summary. Nonzero findings exit with status 1; FDB and unexpected errors exit with status 2.

## State And Persistence Behavior
Most diagnostic paths are read-only, but they deliberately access system keyspaces and sometimes use special keyspace reads. Transactions commonly set `set_read_system_keys`, `set_lock_aware`, and explicit timeouts; repair transactions set `set_access_system_keys`, lock-aware mode, system-immediate priority, and call `update_movekeys_lock_write`.

State observed from FDB includes `\xff/keyServers/`, `\xff/serverKeys/`, `\xff/serverList/`, special keys under `\xff\xff/metrics/`, live status JSON from `fdbcli`, and audit JSON produced by a C++ RPC tool. The script also reads local audit JSON files and may run external binaries with `subprocess.run`.

Dry-run repair only prints planned deletion ranges. Live `serverKeys` repair clears ranges under `SERVER_KEYS_PREFIX + server_id + b'/'`, including the begin boundary key. Live keyServers phantom repair clears specific `\xff/keyServers/<begin>` entries. Before live repair, `main()` disables Data Distribution and acquires the MoveKeys lock through `take_movekeys_lock`; the lock is released and DD restored in a `finally` block.

## Dependencies And Integration Points
The script integrates with FoundationDB's Python API, the local vendored binding in `contrib/metadata_audit/fdb`, `fdb_metadata_utils.py`, `fdbcli`, and the C++ `audit_ss_shards` binary. It assumes FDB metadata key layouts for `keyServers`, `serverKeys`, and `serverList`, and it depends on error-code meanings such as `1037` for `wrong_shard_server`, timeout codes `1007`, `1009`, and `1031`, and `2004` for illegal key ranges.

It also integrates conceptually with FDB Data Distribution internals: KeyRangeMap coalescing invariants, serverKeys ownership transitions, `waitStorageMetrics`, storage server `getShardState` RPC results surfaced by the C++ audit, and MoveKeys lock ownership. The CLI documentation explicitly points operators to `audit_ss_shards -C fdb.cluster --json`, `--report-audit`, `--repair-serverkeys`, and `--repair-keyservers` workflows.

## Risks And Edge Cases
This file is operationally risky because it can mutate core system metadata. The strongest safety gates are explicit repair flags, dry-run default, interactive confirmation for live repair, and MoveKeys locking, but the repair logic still clears metadata ranges based on audit JSON and UID conversions. Incorrect audit files, byte-order assumptions, stale status information, or partial scans could delete valid ownership records.

Several analyses use heuristics: extracting IP addresses from serialized serverList values, matching by UID prefixes, classifying blog/backup/system ranges by key prefix, assuming servers not listed in audit missing ranges have data, and using overlap checks rather than exact range equality. Some scans have fixed limits, so results can be incomplete if metadata exceeds the configured `--limit`.

The Python probing paths can misclassify timeouts as likely missing shards or skip system key ranges that clients cannot probe normally. `verify_all_missing_ranges` samples endpoints and explicitly notes that it can miss gaps in the middle, while `verify_ranges_with_get_range` bounds iteration after reading up to 100 KVs. There is also a possible format pitfall in `repair_serverkeys_from_audit`: it converts `server_id_hex` directly with `hex_to_bytes`, while other audit correlation functions convert C++ UID strings with `uid_cpp_to_raw`; correctness depends on the audit JSON server ID format matching the expected raw bytes.

## Test Signals
Built-in test signals are operational rather than unit-test based. `--test-encoding` round-trips sampled `keyServers` values and reports failures with protocol/shard metadata details. `test_serverkeys_encoding_roundtrip` summarizes observed serverKeys value encodings. `--check-mismatch`, the default wrong-shard scan, direct point probes, metrics probes, and range probes provide independent signals for metadata consistency and DD impact.

Audit JSON integration provides the strongest validation signal because the C++ tool directly asks storage servers for shard state and can include the same metrics path DD uses. Useful regression indicators include no decode errors, no uncoalesced adjacent KRM entries, no empty keyServers source server vectors except the sentinel, no dead live references, no `wrong_shard_server` ranges, successful UID/serverList/running-server correlation, and dry-run repair counts matching audit discrepancies.
