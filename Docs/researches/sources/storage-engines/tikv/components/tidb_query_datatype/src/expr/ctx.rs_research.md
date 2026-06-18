# sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/ctx.rs

## Purpose
This file defines evaluation configuration, SQL execution flags, warning accumulation, and per-evaluation context for TiKV query expressions and codecs.

## Important APIs, types, and functions
`SqlMode` models strict modes, zero date handling, invalid dates, and division-by-zero behavior. `Flag` models DAG request execution flags such as `IGNORE_TRUNCATE`, `TRUNCATE_AS_WARNING`, statement kind flags, `OVERFLOW_AS_WARNING`, `DIVIDED_BY_ZERO_AS_WARNING`, and `IN_LOAD_DATA_STMT`.

`EvalConfig` stores timezone, flags, maximum warning count, SQL mode, paging/max-keys options, division precision increment, and test marker. `from_request` builds it from `tipb::DagRequest`, preferring timezone name over offset. Setter methods update individual config fields, and `new_eval_warnings` creates a bounded warning buffer.

`EvalWarnings` tracks total warning count separately from stored warning details. `append_warning` increments the total and stores up to the configured limit. `merge` combines warning counts and truncates stored details to the receiver capacity.

`EvalContext` combines shared `Arc<EvalConfig>` with mutable warnings. It handles truncation, overflow, division by zero, invalid time errors, string-to-int overflow fallback, warning draining, and unsigned clipping policy.

## Control flow
Error handling methods convert runtime errors to success, warning, or error depending on flags and SQL mode. Truncation is ignored, warned, or returned as an error. Overflow is warned only under `OVERFLOW_AS_WARNING`. Division by zero is statement-sensitive and strict-mode-sensitive. Invalid time errors become hard errors only for strict insert/update/delete paths.

## State and persistence behavior
`EvalConfig` is shared immutably through `Arc`. `EvalContext` owns mutable warnings for a single evaluation path. `take_warnings` atomically replaces the current warning buffer with an empty buffer using the same configured capacity. No durable persistence occurs.

## Dependencies and integration points
The module depends on `tipb::DagRequest`, timezone support in `codec::mysql::Tz`, codec `Error`/`Result`, and `DEFAULT_DIV_FRAC_INCR`. It is used by datum codecs, expression evaluation, aggregate executors, table/index decoders, and executor result warning propagation.

## Risks and edge cases
Warning detail storage is capped while `warning_cnt` keeps growing, so consumers must read both fields. `from_request` silently leaves UTC if neither timezone name nor offset is present. Division-by-zero semantics are subtle: in non-write statements it records a warning. `overflow_from_cast_str_as_int` returns `u64::MAX as i64` for positive overflow, which is `-1` by two's-complement cast and is presumably part of TiDB-compatible cast behavior that should not be casually changed.

## Test signals
Tests cover truncation handling modes, warning count capping, division-by-zero combinations across flags and strict mode, and invalid-time strict write behavior.
