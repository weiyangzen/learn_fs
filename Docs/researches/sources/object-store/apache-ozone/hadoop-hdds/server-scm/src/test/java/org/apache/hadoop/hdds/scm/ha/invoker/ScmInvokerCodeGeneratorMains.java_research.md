# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGeneratorMains.java

Purpose: convenience launcher collection for regenerating production `ScmInvoker` implementations from known SCM replicated APIs. It is package-private test code and is intended for manual execution when an SCM HA handler interface changes.

Important APIs and types: nested classes expose `main(String...)` methods for `DeletedBlockLogStateManager`, `ContainerStateManager`, `PipelineStateManager`, `RootCARotationHandler`, `FinalizationStateManager`, `SecretKeyState`, `SequenceIdGenerator.StateManager`, `StatefulServiceStateManager`, and `CertificateStore`. The nested `All` class runs all generators in a fixed sequence.

Control flow: each nested main delegates directly to `ScmInvokerCodeGenerator.generate(type, true)`, which updates the generated class under the main SCM invoker source directory. `All.main()` chains those individual launchers without arguments.

State and persistence: this file owns no state, but every launcher can mutate checked-in production Java files through the generator. Integration is tightly coupled to the current list of replicated SCM services; adding a new `@Replicate` handler requires adding a corresponding launcher if maintainers want the `All` entry point to cover it. Risks are operational rather than algorithmic: accidentally running a single launcher can leave only part of the invoker set regenerated, and generator output still requires manual import review as documented in the generator.

Test signals: `TestScmInvokerCodeGenerator` covers drift for the same API set. This mains file itself has no assertions; its value is reproducible manual regeneration.
