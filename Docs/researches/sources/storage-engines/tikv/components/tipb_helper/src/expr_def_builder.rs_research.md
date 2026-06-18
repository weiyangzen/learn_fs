# sources/storage-engines/tikv/components/tipb_helper/src/expr_def_builder.rs

Purpose: fluent builder for `tipb::Expr` expression definitions.

Important APIs/types/functions: `ExprDefBuilder` constructors for integer, unsigned integer, real, bytes, decimal, time, duration, null, column reference, scalar function, and aggregate function; `push_child`; `build`; `From<ExprDefBuilder> for Expr`.

Control flow: each constructor creates a default `Expr`, sets `ExprType`, encodes literal bytes with TiKV/TiDB codec helpers, and fills `FieldType` metadata. `push_child` appends nested expressions and returns the builder for chaining.

State and persistence: no persistence; state is the owned protobuf expression under construction.

Dependencies/integration: depends on `codec`, TiDB query datatype accessors/codecs, and `tipb` protobuf types. Used to produce valid TiDB expression trees for coprocessor/query paths and tests.

Risks: constructors unwrap codec writes; incorrect field type metadata can produce expressions that decode but execute incorrectly; `column_ref` casts `usize` to `i64`.

Test signals: no direct tests in this file; validation is indirect via query expression consumers.
