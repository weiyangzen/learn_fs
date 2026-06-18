# sources/storage-engines/tikv/components/tidb_query_codegen/src/rpn_function.rs

Purpose: implements the `#[rpn_fn]` attribute macro that converts plain Rust scalar functions into TiDB RPN evaluator metadata, validators, evaluators, and vectorized row loops.

Important APIs and control flow: `transform` parses attributes and an `ItemFn`, rejects explicit lifetimes, and selects `VargsRpnFn`, `RawVargsRpnFn`, or `NormalRpnFn`. `RpnFnAttr` parses flags such as `varg`, `raw_varg`, `nullable`, `writer`, argument bounds, metadata hooks, extra validator, and captures. Type parsers recognize `Option<&T>`, `Option<JsonRef>`, `BytesRef`, enum/set refs, and writer guard returns. `ValidatorFnGenerator` emits return-type, arity, argument-type, and custom validation. Normal functions generate a dispatch trait, default unreachable impl, real impl over an argument type list, evaluator struct, and `_fn_meta` constructor. Vararg paths generate row loops using thread-local buffers; raw varargs pass `ScalarValueRef` slices.

State and persistence behavior: generated evaluators are stateless apart from metadata boxed behind `Any`, thread-local temporary argument buffers, writer buffers, and per-call chunked result vectors. No durable state is kept.

Dependencies and integration: relies on `syn`, `quote`, `heck`, `tidb_query_expr` function traits, `tidb_query_datatype` evaluable traits, and `tipb::Expr` validation. Generated `RpnFnMeta` values are consumed by the expression framework to validate and execute pushed-down functions.

Risks and test signals: code generation uses specialization, unsafe transmutes to extend row-local references to static within bounded buffers, null-bit-vector fast paths, and metadata downcasts. Attribute combinations have explicit validation, but generated code assumes caller contracts for lifetimes, argument ordering, and output row count. Tests compare generated token streams for normal, generic, capture, and non-null enum cases and verify type parsing/lifetime helpers.
