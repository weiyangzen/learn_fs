# sources/storage-engines/sqlite/ext/misc/prefixes.c

Purpose: implements `prefixes()` table-valued function and `prefix_length()` scalar helper.

Important APIs/types/functions: `prefixes_cursor` stores copied input, byte length, and rowid. Virtual table methods include `prefixesConnect()`, `prefixesBestIndex()`, `prefixesFilter()`, `prefixesColumn()`, and `prefixesEof()`. `prefixLengthFunc()` counts shared UTF-8 character prefixes.

Control flow: best-index prefers equality on hidden `original_string`. Filtering copies input and starts at rowid 0. Each row returns the input truncated to `nStr-rowid`, producing longest-to-empty byte prefixes.

State and persistence: transient per-cursor input copy only.

Dependencies/integration: SQLite eponymous virtual table support and hidden-column constraints; module is innocuous.

Risks/test signals: `prefixes()` truncates by bytes and may split multibyte UTF-8; `prefix_length()` assumes well-formed UTF-8. Test empty/null inputs, multibyte/malformed strings, constrained vs unconstrained plans, row ordering, hidden original column, and prefix length symmetry.
