## sources/test-tools/syzkaller/pkg/kconfig/minimize.go

Purpose: minimizes a kernel config difference while preserving a caller-provided predicate, typically to identify configs responsible for a behavior.

Important APIs/types/functions: `KConfig.Minimize`, `missingConfigs`, `missingLeafConfigs`, `addDependencies`, `CauseConfigFile`, and `writeSuspects`.

Control flow: computes full-vs-base missing `y` tristate configs, reduces to leaf configs, converts candidate subsets into configs by adding dependency closure and non-tristate values, saves each step config through `debugtracer`, runs generic slice minimization, then writes `cause.config` for suspects.

State and persistence: writes debug trace files `step_N.config` and `cause.config` through the supplied tracer. Does not mutate input configs except via clones.

Dependencies and integration: depends on `pkg/bisect/minimize`, `debugtracer`, `maps.Keys`, and dependency data from parsed `KConfig`.

Risks: only minimizes `Yes` tristate additions; modules and non-tristate values are handled coarsely. Dependency closure ignores select conditions and expression semantics, so candidates can be over/under-inclusive. Predicate cost can be high; `maxSteps` bounds attempts.

Test signals: `minimize_test.go` validates expected reduction behavior.
