# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.h

Purpose: Declares the cppsuite cursor-bound helper.

Important APIs/types/functions: `class bound` exposes constructors for explicit and random bounds, `get_config`, `get_key`, `get_inclusive`, `clear`, and `apply(scoped_cursor&)`.

Control flow: interface separates bound construction from cursor application, allowing tests to store and apply lower/upper bounds later.

State and persistence: private state is bound key string, inclusivity flag, and lower/upper flag. Persistence is limited to subsequent cursor behavior after `apply`.

Dependencies/integration: includes `src/storage/scoped_cursor.h`; used by `bound_set` and bound-related tests.

Risks and test signals: no validation in the declaration for key format or empty keys; correctness depends on implementation assertions and WT cursor-bound behavior.
