# sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_eval.rs

## Purpose
This file evaluates an `RpnExpression` against batch input columns and logical row indexes. It defines the stack representation used while walking RPN nodes and implements `RpnExpression::eval`, including lazy column decoding, stack manipulation, scalar/vector argument handling, and vector result production.

## Important APIs, Types, and Control Flow
`RpnStackNodeVectorValue` represents vector values as either generated owned `VectorValue` results or references to decoded input columns plus logical rows. `take_vector_value` materializes references into compact owned vectors by copying selected logical rows. `RpnStackNode` wraps either scalar constants with their `FieldType` or vector nodes with their field type.

`RpnExpression::eval` first calls `ensure_columns_decoded` for every `ColumnRef`, passing schema field types and logical rows into `LazyBatchColumnVec`. It then calls `eval_decoded`, which asserts a nonzero output size at or below `BATCH_MAX_SIZE`, pushes constants and column refs onto a stack, and invokes each function node by slicing the last `args_len` stack entries. The function pointer stored in `RpnFnMeta` receives `EvalContext`, output row count, argument nodes, return field type through `RpnFnCallExtra`, and metadata. The returned `VectorValue` replaces its arguments on the stack.

## State, Dependencies, and Integration
Evaluation mutates only the evaluation context and lazy input columns during decode. Generated vector results live on the stack; referenced columns borrow from caller-owned input. Logical row state is explicit, allowing filtered or reordered rows without reshaping physical columns. Integration points include `tidb_query_codegen::rpn_fn` generated evaluators, `LazyBatchColumnVec`, `VectorValue`, `FieldType`, and expression nodes built by `expr_builder.rs`.

## Risks and Test Signals
The evaluator intentionally panics for structurally invalid RPN, decoded-column mismatches, invalid output row counts, and wrong eval types. Borrowing and logical-row handling are key correctness risks. Tests cover constants, decoded and raw columns, scalar/vector argument combinations, null propagation, parsed tree evaluation, function metadata, `take_vector_value`, invalid expressions, and microbenchmarks for arithmetic, comparison, real, and bytes paths.
