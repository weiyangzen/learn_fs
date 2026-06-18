# sources/object-store/garage/src/format-table/lib.rs

Purpose: formats tab-delimited strings into padded text tables for terminal output.

Important APIs/types/functions: `format_table_to_string(data: Vec<String>) -> String` and `format_table(data: Vec<String>)`.

Control flow: splits each row on tab, computes maximum character width per column, then emits rows with two spaces after every non-last column. `format_table` prints the returned string to stdout.

State and persistence: stateless; output only.

Dependencies and integration points: no external dependencies. Used by CLI modules for bucket/key/layout/status/worker/block/admin-token tables.

Risks: assumes every row has at least one column; an empty string row works as one empty column, but a truly empty data vector produces an empty string. Width uses `chars().count()`, not display width, so East Asian wide characters or ANSI escapes may misalign. The API consumes `Vec<String>`, causing callers to allocate.

Test signals: no unit tests, but many CLI code paths depend on it. Simple examples in docs explain expected input format.
