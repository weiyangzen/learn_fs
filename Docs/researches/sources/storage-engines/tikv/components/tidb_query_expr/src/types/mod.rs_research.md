# sources/storage-engines/tikv/components/tidb_query_expr/src/types/mod.rs

## Purpose
This module is the public facade for the `tidb_query_expr::types` submodule. It wires together the internal RPN expression representation, builder, evaluator stack node, function metadata ABI, and test utilities.

## Important APIs, Types, and Control Flow
The file declares private modules `expr`, `expr_builder`, and `expr_eval`, a public `function` module, and a test-only `test_util` module. It re-exports `RpnExpression`, `RpnExpressionNode`, `RpnExpressionBuilder`, `BATCH_MAX_SIZE`, `RpnStackNode`, `RpnFnCallExtra`, and `RpnFnMeta`. There is no runtime control flow in this file; it controls namespace boundaries and which internals are available to the rest of the crate.

## State, Dependencies, and Integration
This facade is used by expression implementation modules and tests that need to build or evaluate RPN expressions without depending on internal filenames. It keeps the evaluator's `RpnStackNode` visible for generated function glue while keeping helper modules mostly private.

## Risks and Test Signals
The main risk is API surface drift: making internals too private can break generated code or tests, while exporting too much can freeze implementation details. Test signals are indirect through all expression builder, evaluator, and RPN function tests.
