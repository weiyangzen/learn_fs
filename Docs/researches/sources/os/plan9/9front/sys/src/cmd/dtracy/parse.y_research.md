# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/parse.y

This yacc grammar defines the dtracy scripting language. It parses probe clauses, optional predicates, actions, expression statements, printing, formatted printing, and aggregations.

Key grammar features:
- A program is a sequence of clauses.
- Clauses contain one or more probes, an optional `if expr` predicate, and either a default action or `{ ... }`.
- Default action is `print(probe)`.
- Statements include expression evaluation, `print`, `printf`, and aggregation assignments like `@name[key] = agg(value)`.
- Expressions support numeric/string/symbol literals, arithmetic, bitwise operations, comparisons, logical operators, unary operators, ternary, parentheses, and casts.
- Type names include `u8/s8` through `u64/s64` and `string`.

Important implementation notes:
- Predicates are immediately type-checked and bytecode-generated in the grammar action.
- Non-predicate action expressions are type-checked through `exprcheck(..., 0)`, allowing record insertion for runtime value capture.
- Greater-than comparisons are normalized by swapping operands and using less-than operators.
