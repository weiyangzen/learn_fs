# sources/test-tools/syzkaller/prog/expr.go

Purpose: evaluates conditional expressions and maintains conditional union fields during generation, mutation, deserialization, validation, and minimization.

Important APIs/types/functions: `BinaryExpression.Evaluate`, `Value.Evaluate`, `makeArgFinder`, `randGen.patchConditionalFields`, `forEachStaleUnion`, `checkUnionArg`, `matchingUnionArgs`, `Prog.checkConditions`, `ErrViolatedConditions`, `Call.checkConditions`, and `Call.setDefaultConditions`.

Control flow and state: expression evaluation recursively computes boolean/bitwise operators, resolving path-based values through an `ArgFinder`. Conditional patching loops until no stale unions remain, generating replacement args and extra resource-constructor calls as needed. `forEachStaleUnion` walks call args with parent stack, skips `ANY` pointers, evaluates current union options, and reports stale or transient unions with matching alternatives. Default-setting replaces stale unions with default or first matching field defaults until stable.

Dependencies and integration: depends on compiler expression/field metadata, target `findArg`, `SquashedArgFound`, arg replacement, random generation, traversal with parent stack, and minimization integer reset logic.

Risks: nested conditional patching is guarded by a depth panic. Missing matching union fields panic because descriptions should include a fallback. Expressions that reference squashed `ANY` args are treated as uncalculable, preserving existing choices. Incorrect default elision can silently violate conditions.

Test signals: `expr_test.go` covers generation, mutation, strict validation errors, conditional resource stress, minimization interactions, nested conditions, conditional unions, and serialize/deserialize preservation of default selected options.
