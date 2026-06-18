# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConvertUTF.h

Purpose: Provides Unicode conversion declarations between UTF-8, UTF-16, and UTF-32, imported from the Unicode sample implementation, plus legality checking for UTF-8 sequences.

Important APIs/types/functions: Defines `UTF32`, `UTF16`, `UTF8`, `Boolean`, Unicode maximum/replacement constants, `ConversionResult` (`conversionOK`, `sourceExhausted`, `targetExhausted`, `sourceIllegal`), and `ConversionFlags` (`strictConversion`, `lenientConversion`). C-linkage functions convert UTF8/16/32 in every direction and update source/target pointers in place. `isLegalUTF8Sequence()` validates a bounded UTF-8 sequence.

Control flow: Callers pass pointer-to-current source and target positions plus end pointers. Conversion proceeds until input is exhausted, target is full, or an illegal/incomplete sequence is found. On return the pointers identify the last successfully converted positions or the problematic source start.

State and persistence behavior: Stateless buffer conversion only; no persistent data. Strict mode rejects irregular sequences and isolated surrogates; lenient mode converts some irregular/surrogate cases but still rejects illegal sequences and handles over-maximum values per documented behavior.

Dependencies and integration points: Standalone C-compatible header with no FDB-specific dependency. Used wherever FoundationDB needs portable UTF validation/conversion without relying on platform `wchar_t`.

Risks: Callers must allocate sufficient target buffers and handle pointer advancement after partial conversion. Lenient mode can hide invalid Unicode shape that strict callers may require. The typedefs assume unsigned fixed minimum widths but not exact platform-native Unicode types.

Test signals: Round trips among UTF-8/16/32; strict rejection of malformed UTF-8, overlong forms, isolated surrogates, and code points above U+10FFFF; target exhaustion and source exhaustion pointer behavior; lenient replacement-character behavior; C and C++ linkage builds.
