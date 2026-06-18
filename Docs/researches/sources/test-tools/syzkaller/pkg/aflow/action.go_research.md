# sources/test-tools/syzkaller/pkg/aflow/action.go

Purpose: Core action abstraction for the `aflow` package.

Important APIs and control flow: `Action` requires unexported `verify(*verifyContext)` and `execute(*Context) error` methods, restricting implementations to the package or types that can satisfy those unexported names in-package. `pipeline` stores ordered `Action`s. `Pipeline(actions ...Action)` constructs a pipeline. `(*pipeline).execute` runs actions sequentially and stops on the first error. `(*pipeline).verify` calls every action's verifier in order.

State and dependencies: `pipeline.actions` is immutable by convention after construction but not defensively copied. Execution state lives in the passed `Context`; validation state lives in `verifyContext`.

Integration points: other `aflow` actions compose through `Pipeline` to express ordered automation flows while allowing dataflow through shared context variables, args, instructions, or prompts.

Risks and tests: because verification visits all actions even if earlier verification records errors, `verifyContext` must aggregate/report consistently. Because execution short-circuits on errors, later actions may not run cleanup unless modeled separately. Test signals are package tests for concrete actions and pipeline composition.
