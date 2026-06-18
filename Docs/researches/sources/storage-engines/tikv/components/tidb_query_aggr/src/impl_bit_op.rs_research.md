# Research: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_bit_op.rs

## sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_bit_op.rs

Purpose: implements BIT_AND, BIT_OR, and BIT_XOR aggregate functions through a shared `BitOp` trait and generic aggregate state.

Important APIs are `BitOp`, macro-generated marker types `BitAnd`, `BitOr`, `BitXor`, `AggrFnDefinitionParserBitOp<T>`, `AggrFnBitOp<T>`, and `AggrFnStateBitOp<T>`. Each operation declares its `ExprType`, initial state, and in-place u64 operation. The parser verifies expression type, checks one child, emits the root field type as the output schema, rewrites the child expression for bit operations, and returns the generic aggregate.

Control flow updates ignore NULLs and apply the operation to `self.c` using the input `Int` cast to `u64`; result is pushed back as TiDB `Int`. BIT_AND starts at all ones, OR and XOR at zero, matching SQL aggregate behavior for empty/all-null inputs. State is a single `u64`; no persistence.

Dependencies include aggregate codegen, datatype vectors, RPN expression rewriting, EvalContext, and `tipb`. Risks include signed/unsigned casting semantics for negative values, schema/root field type trust, and ensuring expression rewriting converts supported child types into integer-compatible values. Test signals cover initial/NULL behavior, repeated and vector updates, negative value wraparound, and integration parsing/evaluation for all three bit operations.
