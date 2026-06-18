# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyArgs.java

Purpose: focused regression test for `OmKeyArgs.toBuilder()` preserving the `headOp` flag.

Important APIs/types/functions: uses `OmKeyArgs.Builder.setHeadOp`, `build`, `isHeadOp`, and `toBuilder`.

Control flow and state: a parameterized boolean test builds `OmKeyArgs` with both true and false `headOp` states, then rebuilds via `toBuilder` and asserts the flag is unchanged.

Dependencies and integration points: `headOp` affects key metadata/read request behavior, especially HEAD-like operations that should not be treated as normal reads in higher layers.

Risks and test signals: protects against builder copy omissions when adding or refactoring fields in `OmKeyArgs`. Any new boolean flags with request semantics should get similar toBuilder coverage.
