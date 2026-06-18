# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/mod.rs

Purpose: top-level MySQL codec module facade and fractional-second precision helper.

Important APIs/types/functions: constants `UNSPECIFIED_FSP`, `MAX_FSP`, `MIN_FSP`, `DEFAULT_FSP`, `DEFAULT_DIV_FRAC_INCR`; function `check_fsp`; public submodules and re-exports for decimal, duration, enum, JSON, set, time, and vector types/codecs.

Control flow: `check_fsp` maps unspecified precision to the default, validates the inclusive range 0..=6, and returns a `u8` precision or invalid-type error.

State and persistence: no state. It is a module boundary and pure validation helper.

Dependencies and integration points: used throughout MySQL time/duration/JSON conversion code to normalize fsp. The re-export list is the public import surface for consumers of `codec::mysql`.

Risks: changes to re-exports can break many downstream imports. FSP validation is tiny but central to temporal correctness. No local tests in this file; coverage is indirect through time/duration/JSON temporal tests.
