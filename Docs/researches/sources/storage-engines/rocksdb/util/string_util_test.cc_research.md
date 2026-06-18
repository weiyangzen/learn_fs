# sources/storage-engines/rocksdb/util/string_util_test.cc

## Purpose

Provides focused tests for two string utility behaviors: compact numeric formatting and trimming.

## APIs, control flow, and state

`NumberToHumanString` assertions cover `INT64_MIN`, `INT64_MAX`, zero, boundaries below/at K/M/G thresholds, and negative equivalents. `Trim` assertions cover empty strings, no whitespace, leading whitespace, trailing whitespace, both ends, interior whitespace preservation, and all-whitespace inputs.

## Dependencies and integration

It includes `string_util.h`, gtest, stack trace support, and test utilities. There is no persistent state or external IO.

## Risks and test signals

The tests signal expected truncation-style K/M/G formatting and correct all-whitespace handling. They do not cover byte formatting, micros formatting, option escaping, numeric parser suffixes, time parsing, or portable `errnoStr`.
