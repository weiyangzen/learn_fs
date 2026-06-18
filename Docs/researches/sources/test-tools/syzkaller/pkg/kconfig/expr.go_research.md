## sources/test-tools/syzkaller/pkg/kconfig/expr.go

Purpose: represents and parses Kconfig dependency expressions.

Important APIs/types/functions: `expr` interface and implementations `exprShell`, `exprNot`, `exprIdent`, `exprString`, `exprBin`; `binOp`; `exprAnd`; parser methods `parseExpr`, `parseExprAnd`, `parseExprCmp`, and `parseExprTerm`.

Control flow: recursive descent parser implements precedence for OR, AND, comparisons, unary not, parentheses, quoted strings, shell expressions, and identifiers. Dependency collection records only identifiers reached through binary expressions; negation intentionally does not collect dependencies.

State and persistence: expression objects are stored on `Menu` nodes in `kconfig.go`.

Dependencies and integration: depends on the generic line parser in `parser.go`; used for `depends on`, `visible if`, defaults, ranges, and prompts.

Risks: does not evaluate expressions, only extracts dependencies. Negated dependencies are ignored by `exprNot.collectDeps`, which may understate dependency closure. Kconfig’s nuanced tristate semantics are not modeled.

Test signals: `expr_test.go` covers parsing/stringification and fuzz entry points.
