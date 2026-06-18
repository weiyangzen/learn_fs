# sources/storage-engines/rocksdb/util/string_util.h

## Purpose

Declares shared utilities for string splitting, numeric formatting/parsing, option escaping, prefix/suffix checks, time range parsing, and errno string conversion.

## APIs, control flow, and state

The header exposes function APIs plus two templated helpers: `PutBaseChars` writes fixed-width digits in an arbitrary base up to 36 and advances the buffer pointer, while `ParseBaseChars` reads fixed-width digits into a `uint64_t` without overflow checks. It also declares `kNullptrString` and parser functions for booleans, integer widths, doubles, `size_t`, vectors, and time strings.

## Dependencies and integration

It depends on standard string/vector/map headers and `rocksdb/rocksdb_namespace.h`, with a forward declaration of `Slice`. It is included by many low-level files, including `slice.cc`, `threadpool_imp.cc`, and option parsing code.

## Risks and test signals

The parser declarations throw exceptions for invalid numeric conversions rather than returning `Status`. `ParseBaseChars` explicitly returns modulo-2^64 results on overflow. Tests in this subset cover only part of the surface: human integer formatting, trimming, and base formatting.
