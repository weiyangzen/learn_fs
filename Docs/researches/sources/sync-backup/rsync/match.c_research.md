# sources/sync-backup/rsync/match.c

## Purpose
`match.c` implements rsync's rolling-checksum block matching on the sender side. It scans the sender's file against checksums supplied by the receiver/generator and emits literal data plus match tokens, while computing the final whole-file transfer checksum.

## Important APIs, Types, and Functions
Public functions are `match_sums()` and `match_report()`. Internal helpers are `build_hash_table()`, `matched()`, and `hash_search()`. Important state includes `updating_basis_file`, `sender_file_sum`, per-file counters (`false_alarms`, `hash_hits`, `matches`, `data_transfer`), and cumulative counters for debug reporting.

## Control Flow
`match_sums()` initializes checksum state, handles append modes by skipping already-present basis data, builds a hash table for receiver checksums when available, and either runs `hash_search()` or sends literal chunks. `build_hash_table()` chooses a traditional 64K hash table or a larger odd table sized for about 80 percent load, then chains sum entries by weak checksum. `hash_search()` rolls the weak checksum byte by byte, checks candidate chains, computes strong sums lazily, prefers adjacent `want_i` matches for run-length token efficiency, and has special alignment logic for in-place updates. `matched()` sends pending literal data and optional match token, updates the running whole-file checksum, advances `last_match`, and emits progress.

## State and Persistence
The matching state is in process memory. Persistent transfer effects are protocol writes through `send_token()` and `write_buf()`. `stats.literal_data` and `stats.matched_data` are updated, and `sender_file_sum` is written to the peer. If the mapped file reports a read error, the final checksum is intentionally corrupted to force receiver-side detection.

## Dependencies and Integration Points
The file depends on rsync checksum routines (`get_checksum1()`, `get_checksum2()`, `sum_init()`, `sum_update()`, `sum_end()`), memory mapping (`map_ptr()`), token IO, progress output, and `stats`. It is called from sender file-transfer code after the receiver's block sums are available.

## Risks
Rolling checksum correctness and offset arithmetic are critical. In-place updates require avoiding matches to basis chunks that have already been overwritten unless they are known same-offset. Hash-chain mutation in that mode changes future candidate searches. Large files rely on table sizing and `OFF_T`/`int32` conversions. Read-error checksum corruption must never accidentally equal the real checksum.

## Test Signals
Tests should verify identical-file tokenization, literal-only transfers, shifted blocks, adjacent match preference, append and append-verify modes, in-place updates with zero blocks, large files using the expanded hash table, progress updates, false alarm counting, and forced checksum mismatch after a read error.
