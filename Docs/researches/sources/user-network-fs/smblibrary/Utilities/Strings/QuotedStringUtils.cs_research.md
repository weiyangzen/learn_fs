# sources/user-network-fs/smblibrary/Utilities/Strings/QuotedStringUtils.cs

Purpose: `QuotedStringUtils` provides simple quote wrapping, unwrapping, searching, and splitting while ignoring separators inside double quotes.

Important APIs/types/functions: `Quote`, `Unquote`, `IsQuoted`, `IndexOfUnquotedChar`, `IndexOfUnquotedString`, and `SplitIgnoreQuotedSeparators`.

Control flow: quote checks look at first/last characters. Search methods toggle an `inQuote` boolean on every `"` and match only outside quotes. Split repeatedly finds unquoted separators and applies optional `RemoveEmptyEntries`.

State and persistence behavior: stateless string utility.

Dependencies and integration points: general parser helper for command/config-like strings.

Risks: escaped quotes are not supported, unmatched quotes simply keep `inQuote` true through the end, and `IndexOfUnquotedString` repeatedly calls `Substring(index)`, which is less efficient. Null inputs are not handled.

Test signals: quoted and unquoted separators, empty entries, unmatched quotes, escaped quote expectations, multi-character string search, and null/empty strings.
