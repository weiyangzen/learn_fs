# sources/test-tools/fio/json.c

Purpose: small JSON object model and pretty-printer for fio output. It creates objects/arrays/values, attaches values to parents, escapes strings, frees full trees, and writes formatted JSON into a `buf_output`.

Important APIs/functions: `json_create_object`, `json_create_array`, `json_object_add_value_type`, `json_array_add_value_type`, `json_free_object`, and `json_print_object`. Static constructors handle integer, float, string, object, and array value types; `strdup_escape` escapes backslash and double quote for string output.

Control flow: add-value functions clone scalar/string values or wrap an existing object/array, create parent pairs or array entries, then grow pointer arrays with `realloc`. Printing computes indentation by walking parent pointers and recursively prints objects, arrays, pairs, and scalar values.

State/persistence: owns heap-allocated `json_object`, `json_array`, `json_pair`, value nodes, string copies, and dynamic child arrays. No file persistence occurs directly; output accumulates in `struct buf_output`.

Dependencies/integration: uses `json.h`, `log.h`, and `buf_output` through `log_buf`. It is integrated with fio's normal JSON output paths rather than a general JSON parser.

Risks/test signals: allocation failures are surfaced as `ENOMEM`, but object/array wrapping transfers ownership expectations to the JSON tree. String escaping only covers backslash and quote, not control characters. Tests should cover nested ownership/free, array/object parent levels, null-string handling through inline wrappers, and valid escaping.
