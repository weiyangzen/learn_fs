# sources/storage-engines/tikv/cmd/tikv-ctl/src/util.rs

## Purpose
`util.rs` contains small shared helpers for `tikv-ctl`: logger initialization, explicit operator confirmation, hex decoding, byte-size formatting, error-and-exit, and key-range intersection checks.

## Important APIs, Types, And Functions
- `init_ctl_logger(level, format)` creates a default `TikvConfig`, routes RocksDB/raftdb info logs to `./ctl-engine-info-log`, chooses JSON or text log format, and calls `server::setup::initial_logger`.
- `warning_prompt(message)` requires the exact input `I consent`.
- `from_hex` accepts plain hex or `0x`/`0X` prefixed hex.
- `convert_gbmb` formats byte counts as bytes, MiB, or GiB plus MiB.
- `perror_and_exit` prints a prefixed error and exits gracefully.
- `check_intersect_of_range` checks whether two left-closed, right-open TiKV key ranges overlap, treating empty endpoints as unbounded.

## Control Flow
The helpers are direct and side-effect-light except for logger initialization, stdin prompting, and process exit. `check_intersect_of_range` first rejects when the region end is before or equal to the limit start, then rejects when the limit end is strictly before the region start; otherwise it reports an intersection.

## State And Persistence Behavior
The logger setup writes engine info logs under `./ctl-engine-info-log`. `warning_prompt` gates commands that may expose plaintext data or keys but does not persist consent.

## Dependencies And Integration Points
Used by `main.rs` and `executor.rs`. It depends on `kvproto::kvrpcpb::KeyRange`, `server::setup::initial_logger`, `TikvConfig`, `tikv_util::config::LogFormat`, `hex`, and raftstore test helpers.

## Risks And Edge Cases
- `init_ctl_logger` panics for invalid log level or format.
- `warning_prompt` trims only newline, not carriage return; Windows-style input may not match.
- `convert_gbmb` returns an empty string for exactly zero GiB after MiB path only below MiB returns bytes, so larger exact multiples are handled as GiB with trailing space trimmed by composition.

## Test Signals
Unit tests cover `from_hex` prefixes and range-intersection cases including unbounded endpoints, exact boundary behavior, partial overlap, containment, and last-region semantics.
