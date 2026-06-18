## sources/test-tools/syzkaller/pkg/kconfig/expr_test.go

Purpose: verifies expression parser behavior and fuzzes it for panics.

Important APIs/types/functions: `TestParseExpr` and `TestFuzzParseExpr`.

Control flow: test cases parse expressions with identifiers, logical ops, comparisons, strings, shell expansions, negation, and parentheses, then compare string output. Fuzz test feeds arbitrary data through `FuzzParseExpr`.

State and persistence: none.

Dependencies and integration: exercises parser primitives and expression nodes together.

Risks: stringification equivalence is not semantic evaluation. Fuzz test likely checks non-crashing behavior more than correctness.

Test signals: useful coverage for precedence and malformed input tolerance.
