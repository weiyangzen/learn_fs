# sources/storage-engines/foundationdb/contrib/SimpleOpt/include/SimpleOpt/SimpleOpt.h

Purpose: vendored SimpleOpt 3.4, a portable single-header C++ command-line parser supporting short/long/word options, optional/required/multiple arguments, clumped short options, partial matching, case-insensitive matching, and Windows slash conversion.

Important APIs/types: enums `ESOError`, `_ESOFlags`, and `ESOArgType`; option descriptor `CSimpleOptTempl<SOCHAR>::SOption`; aliases `CSimpleOptA`, `CSimpleOptW`, and `CSimpleOpt`. Public methods include `Init`, `SetOptions`, `SetFlags`, `HasFlag`, `Next`, `Stop`, `LastError`, `OptionId`, `OptionText`, `OptionArg`, `OptionSyntax`, `MultiArg`, `FileCount`, `File`, and `Files`.

Control flow: `Next()` scans `argv`, normalizes slash options on Windows, handles combined `=` args, short arg forms, clumps, invalid options, and required separated args. Non-options are shuffled behind unprocessed args, preserving file order for `Files()`. `LookupOption` uses exact or best partial matching; `MultiArg` validates required arguments.

State and persistence: parser mutates the caller-provided `argv` array and may allocate a shuffle buffer when argc exceeds `SO_STATICBUF` unless `SO_MAX_ARGS` forces static operation.

Dependencies and integration: header-only C++ with optional C runtime use. FoundationDB includes it via the contrib CMake include path.

Risks and test signals: mutating `argv` surprises callers; partial matching can be ambiguous; `Copy` disables ASAN due overlapping moves; Unicode/MBCS support is limited. Tests should cover ambiguous prefixes, clumped flags, `SO_O_NOERR`, `SO_MULTI`, Windows slash behavior, and file ordering.
