# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/TestScmInvokerCodeGenerator.java

Purpose: regression test ensuring generated SCM HA invoker source files are up to date with their handler interfaces and with `ScmInvokerCodeGenerator` behavior.

Important APIs and types: `runTest(Class<?>)` creates a generator, emits the class body, calls `updateFile(..., overwrite=false)` against `src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/`, and asserts the returned file is null. Individual JUnit tests cover the known replicated handlers: deleted block log, container state, pipeline state, root CA rotation, finalization state, secret key state, sequence ID state manager, stateful service state manager, and certificate store.

Control flow: each test delegates to the shared helper. `updateFile` writes a temporary candidate and returns null only when the candidate MD5 matches the existing checked-in generated invoker. Any API drift, generator formatting change, or stale generated source produces a non-null temp file and fails with a message naming the affected invoker class.

State and persistence: the test may create temporary candidate files in the production invoker directory when output differs because it passes `overwrite=false`; unchanged outputs are deleted by the generator. The test relies on execution from the module working directory because `DIR` is relative. Risks include brittle failures after legitimate API changes until generated files are refreshed, and sensitivity to import/header preservation in the existing generated files.

Integration points: this is the CI signal protecting SCM HA Ratis dispatch code from silently diverging from handler interfaces.
