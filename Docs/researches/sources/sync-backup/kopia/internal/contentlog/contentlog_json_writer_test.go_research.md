# sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer_test.go

Purpose: validates `JSONWriter` output for object/list structure, scalar types, string escaping, time formatting, edge numeric values, and control characters.

Important APIs/types/functions: tests for empty objects, all types, int/uint field and element variants, null/error/time fields, list writing, string escaping raw output, and exhaustive control-character handling.

Control flow: tests construct JSON through writer methods, parse with `encoding/json`, compare maps/slices, and inspect raw output for escape sequences.

State and persistence behavior: in-memory only. Tests exercise writer reuse only through `NewJSONWriter`/`Release`, not cross-call buffer aliasing.

Dependencies/integration: uses `encoding/json`, `strings`, `time`, `os.Stdout` in one debug encode, and `testify/require`.

Risks/test signals: the file includes an older test comment describing unescaped control-character behavior, while later tests require proper `\u00XX` escaping; the current implementation matches the stronger later expectations. Numeric comparisons through `map[string]any` lose integer precision by converting to `float64`.
