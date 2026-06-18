# sources/user-network-fs/samba/source3/utils/net_idmap_check.c

## Purpose
This file implements `net idmap check`, a consistency checker and optional repair tool for classic idmap TDB databases. It validates key/value formats, reciprocal SID-to-ID mappings, database version, and high-water marks, then optionally commits a generated diff.

## Important APIs, Types, And Control Flow
The exported API is `net_idmap_check_db()`. Internal `enum DT` classifies records as SID, UID, GID, HWM, version, sequence, or invalid. `struct record` stores parsed key/value data and extracted SID or numeric ID. `struct check_actions` encodes interactive prompts, automatic actions, defaults, and verbose formatting. `struct check_ctx` holds the input db, in-memory diff db, options, counters, and computed UID/GID HWMs. `parse_record()` recognizes NUL-terminated `S-*`, `UID n`, `GID n`, `USER HWM`, `GROUP HWM`, `IDMAP_VERSION`, and `__db_sequence_number__` records. `traverse_check()` validates each record, detects missing or mismatched reverse links, updates HWM targets, and records diff operations through `add_record()`/`del_record()`. `check_version()` and `check_hwm()` add repair diffs for missing/wrong metadata. `check_commit()` lists or commits diffs through `traverse_commit()`.

## State And Persistence
Input data is read from a dbwrap TDB database. Proposed repairs are staged in a private in-memory rbt db as `TDB_DATA_diff` records containing old and new values. With `--lock`, the input database is opened writable and held in a transaction across check and commit. Without lock, checking is read-only first and the database is reopened writable only for commit. `--test` cancels the write transaction after exercising commit logic.

## Dependencies And Integration Points
The checker depends on dbwrap, dbwrap_rbt, TDB utility helpers, SID parsing, command-line interaction helpers, string quoting/parsing helpers (`cbuf`, `srprs`), and `struct check_options` from `net_idmap_check.h`. It is called only from `net_idmap.c`.

## Risks And Test Signals
Interactive mode requires a TTY unless `--auto` is used. Automatic repair deletes invalid records and fixes missing reverse links; with `--force`, it can commit after concurrent-change warnings. `unpack_diff()` asserts exact packed sizes, so corrupt diff records would abort. HWM repair computes max seen ID plus one, which should be verified against allocation semantics. Test corrupt non-NUL keys, one-way mappings, mismatched reverse mappings, missing/wrong version, low/missing HWMs, concurrent modification before commit, `--repair`, `--auto`, `--force`, `--test`, and `--lock`.
