# sources/storage-engines/sqlite/ext/misc/noop.c

Purpose: registers pass-through test functions used to exercise SQLite scalar function flags and value typing.

Important APIs/types/functions: `noopfunc()` returns its argument unchanged. `multitypeTextFunc()` first materializes text then returns the original value. `sqlite3_noop_init()` registers `noop`, `noop_i`, `noop_do`, `noop_nd`, and `multitype_text` with different deterministic/innocuous/direct-only flags.

Control flow: each call asserts one argument and uses `sqlite3_result_value()`. Registration flag differences drive planner and trusted-schema behavior.

State and persistence: no state.

Dependencies/integration: SQLite scalar function registration and function flag semantics.

Risks/test signals: behavior depends on SQLite security/planner rules rather than internal complexity. Test value preservation for all storage classes, deterministic expression use, direct-only rejection from schema contexts, innocuous behavior under restricted settings, and `multitype_text()` with `typeof()`/numeric comparisons.
