# sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer.go

Purpose: implements a pooled JSON writer optimized for direct, low-allocation construction of log entries and parameter values.

Important APIs/types/functions: `JSONWriter`, `ParamWriter`, object/list methods, field/element writers for strings, ints, uints, bools, null, errors, times, `RawJSONField`, `NewJSONWriter`, `Release`, `Result`, and `GetBufferForTesting`.

Control flow: writer methods maintain a current separator and a stack of enclosing separators. Fields call `beforeField`; array elements call `beforeElement`. Strings are escaped byte by byte, with standard escapes and `\u00XX` escapes for control characters below space. Times are formatted manually as UTC microsecond timestamps.

State and persistence behavior: state is an internal byte buffer, separator, and separator stack returned to a `freepool`. Callers must not retain/mutate writer state after `Release`; logger output receives the byte slice before release.

Dependencies/integration: used by `contentlog.Logger`, `logparam`, and content-specific params.

Risks/test signals: `RawJSONField` trusts callers to provide valid JSON. String iteration is byte-oriented, which is fine for UTF-8 pass-through but must preserve multi-byte data. Tests cover JSON validity, escaping, numeric/time values, nesting, and control-character output.
