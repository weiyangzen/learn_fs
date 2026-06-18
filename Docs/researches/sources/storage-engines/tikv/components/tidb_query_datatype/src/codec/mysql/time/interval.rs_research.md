# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/interval.rs

Purpose: parses MySQL interval literals and converts scalar expression values into normalized interval strings for date/time arithmetic and duration extraction.

Important APIs/types/functions: `IntervalUnit`, `IntervalUnit::from_str`, `is_valid_for_timestamp`, `is_clock_unit`, internal `TimeIndex`, `Interval`, `Interval::parse_from_str`, `extract_duration`, `negate`, accessors, and trait `ConvertToIntervalStr` for `BytesRef`, `i64`, `Real`, and `Decimal`. Static regex/map state includes `ONE_TO_SIX_DIGIT_REGEX`, `NUMERIC_REGEX`, `INTERVAL_REGEX`, and `INTERVAL_STR_INDEX_MAP`.

Control flow: simple units parse an integer part, optional fractional part, rounding behavior, overflow checks, and convert into months, seconds, nanoseconds, and fsp. Compound units use regex numeric extraction, right-align matched numeric fields into a canonical year/month/day/hour/minute/second/microsecond array, validate field count, apply sign, and checked arithmetic. `extract_duration` reuses parsing in strict duration mode and maps month units to 30-day durations where allowed. Conversion implementations normalize different SQL value types before parsing; strings use truncation warnings, `SECOND` strings parse as decimals, reals honor requested decimal formatting, and decimals transform decimal points into unit-specific separators for compound units.

State and persistence: no persistent state beyond lazily initialized regexes/maps. Each `Interval` stores normalized `month`, `sec`, `nano`, and `fsp`.

Dependencies and integration points: depends on duration constants/limits, `Decimal`, `Real`, `BytesRef`, `EvalContext` warning/error policy, `RoundMode`, `lazy_static`, and `regex`. It is consumed by temporal expression evaluation for `INTERVAL` arithmetic and duration conversion.

Risks: MySQL interval grammar is compatibility-heavy; regex extraction tolerates separators by position rather than strict token grammar. Overflow handling differs between normal parse mode, which may return `Ok(None)` after context handling, and duration mode, which returns errors. Fractional parsing truncates to six digits and some simple non-second units round the integer value while also reporting invalid fractional usage. Tests are extensive for unit classification, value-to-string conversion, simple and compound parsing, invalid/overflow cases, and duration extraction.
