# sources/storage-engines/tikv/components/tipb_helper/src/lib.rs

Purpose: crate facade for `tipb_helper`.

Important APIs/types/functions: private `expr_def_builder` module and public `ExprDefBuilder` re-export.

Control flow: no runtime behavior beyond module export.

State and persistence: none.

Dependencies/integration: gives callers a compact import path for expression construction helpers.

Risks: public surface is intentionally tiny; adding helpers requires preserving the builder’s protobuf correctness.

Test signals: no local tests.
