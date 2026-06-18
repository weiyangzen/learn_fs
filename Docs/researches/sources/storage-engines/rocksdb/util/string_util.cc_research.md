# sources/storage-engines/rocksdb/util/string_util.cc

## Purpose

Implements common string, number, size, time, escaping, parsing, and portable errno formatting utilities used across RocksDB.

## APIs, control flow, and state

`StringSplit` uses `std::getline`. Human-format helpers format microseconds, bytes, integers, and local times. Escaping helpers encode non-printable slices as `\xNN`, option strings escape `\`, `#`, `:`, CR, and LF, and unescape reverses CR/LF aliases. Numeric parsers wrap `stoi/stoll/stoull/stod` or C alternatives on Cygwin and apply `K/M/G/T` binary shifts. Vector parsing/serialization uses colon delimiters. Time parsing accepts `HH:mm` and `HH:mm-HH:mm`. `errnoStr` wraps platform-specific `strerror_r`/`strerror_s` behavior.

## Dependencies and integration

It depends on `port/port.h`, `port/sys_time.h`, and `rocksdb/slice.h`. These helpers feed option parsing, diagnostics, metrics formatting, transform registry parsing, and error messages.

## Risks and test signals

Risks include suffix parsing accepting trailing unknown text after the first numeric token, signed shifts overflowing for large parsed values, locale/time dependence, and `trim` calling `isspace` on plain `char`. `string_util_test.cc` covers `NumberToHumanString` boundaries and `trim`; `slice_test.cc` covers base-character formatting.
