# sources/test-tools/syzkaller/prog/expr_test.go

Purpose: validates conditional-field generation, mutation, evaluation, minimization, nesting, and serialization stability.

Important APIs/types/functions: tests include `TestGenerateConditionalFields`, `TestConditionalResources`, `TestMutateConditionalFields`, `TestEvaluateConditionalFields`, `TestConditionalMinimize`, `TestConditionalUnionFields`, `TestNestedConditionalCall`, `TestDefaultConditionalSerialize`, plus helpers `genConditionalFieldProg`, `validateConditionalProg`, and `parseConditionalStructCall`.

Control flow and state: tests generate and mutate programs using test target descriptions, inspect union selections against mask bits, and assert strict deserialization rejects violated conditions with `ErrViolatedConditions`. Minimization tests use predicates that force condition-aware defaulting or retention.

Dependencies and integration: uses `newRand`, `newState`, `ChoiceTable`, `Deserialize`, `Serialize`, `Minimize`, `testify`, and conditional descriptions in the `test/64` target.

Risks: random coverage thresholds are modest and can miss rare conditional combinations, but deterministic table cases cover core semantics. Exact serialized output makes default-elision behavior explicit.

Test signals: strong coverage for parent-path expressions, nested conditional structs, conditional unions, transient defaults, mutation sanitation, and minimizer interaction with condition-changing integer resets.
