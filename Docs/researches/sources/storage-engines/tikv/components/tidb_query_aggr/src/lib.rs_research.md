# sources/storage-engines/tikv/components/tidb_query_aggr/src/lib.rs

Purpose: defines the aggregate-function framework for TiDB batch executors. It exposes parser entry points, declares aggregate modules, and provides the traits/macros that let concrete aggregate states be boxed while still receiving typed updates.

Important APIs and control flow: `AggrFunction` exposes `name` and `create_state`; `AggrFunctionState` is the object-safe state surface with typed update-partial supertraits for every supported eval reference and a `push_result` method. `ConcreteAggrFunctionState` is the simpler trait concrete states implement. Specialization provides a default "unmatched parameter type" panic implementation and a matching implementation that routes to `update_concrete_unsafe`, `update_repeat_unsafe`, and `update_vector_unsafe`.

State and persistence behavior: all aggregation state is per boxed state object and in memory. The module does not persist state; it defines how callers update rows, repeated rows, and vectors, then push results into `VectorValue` columns.

Dependencies and integration: uses nightly features (`specialization`, `proc_macro_hygiene`, `stmt_expr_attributes`) and `tidb_query_codegen::AggrFunction` in concrete modules. Macros `update!`, `update_vector!`, and `update_repeat!` are the call-site adapters for unsafe type erasure.

Risks and test signals: runtime type mismatch intentionally panics rather than returning `Result`, so parser/schema correctness is critical. Unsafe conversions are hidden behind macros and specialization; future eval type additions must update trait bounds and unmatched impls. Tests verify successful matching, repeated `push_result`, and panic behavior for wrong parameter/result targets.
