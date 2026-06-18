# sources/storage-engines/tikv/components/tikv_util/src/log.rs

## Purpose
Defines TiKV's global logging macros and helpers for formatting slog logger key/value context in panic or error strings.

## Important APIs, Types, And Functions
Macros `crit!`, `warn!`, `info!`, `debug!`, and `trace!` forward to `slog_global`. The custom `error!` macro supports `?err` and `%err` forms and appends `err_code` via `error_code::ErrorCodeExt`; `error_unknown!` does the same with `error_code::UNKNOWN`. `info_or_debug!` and `info_or_error!` choose a log level by condition.

`SlogFormat<'a>` implements `Display` for a logger's owned key/value list. `format_kv_list` serializes borrowed values before owned logger values. `slog_panic!` panics with a message plus formatted slog context.

## Control Flow
Logging macros expand directly into `slog_global` calls. Error macros have special arms for literal-only and full slog argument forms so the error and error code fields are appended correctly. `FormatKeyValueList` serializes slog values as `[key=value]` tokens, inserting spaces after the first token. `slog_panic!` builds the combined context string and omits the trailing context when empty.

## State And Persistence
The file has no owned persistent state. It reads logger key/value state through slog APIs and emits logs through the global logger.

## Dependencies And Integration
Depends on `slog`, `slog_global`, and `error_code`. It integrates with `logger/mod.rs` formatting and with all TiKV code using crate-level logging macros.

## Risks
The specialized `error!` macro expects errors to implement `ErrorCodeExt`; callers without that trait must use `error_unknown!` or regular slog form. Formatting panics use `unwrap` internally while serializing slog values, which is acceptable for diagnostic code but could panic if an unusual serializer error occurred.

## Test Signals
Tests verify empty and nested logger key/value formatting order and `slog_panic!` output with no context, borrowed context, owned context, and combined borrowed plus owned context.
