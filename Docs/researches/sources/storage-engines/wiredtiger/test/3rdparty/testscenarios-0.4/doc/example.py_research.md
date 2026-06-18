# sources/storage-engines/wiredtiger/test/3rdparty/testscenarios-0.4/doc/example.py

Purpose: small documentation example showing how a unittest-style test can be multiplied by scenarios through `TestWithScenarios`.

Important APIs, types, and functions: imports `TestWithScenarios`; defines `scenario1`, `scenario2`, and `SampleWithScenarios`. `SampleWithScenarios.scenarios` supplies two `(name, parameter_dict)` tuples. `test_demo()` asserts that the injected `attribute` is a string.

Control flow: when loaded by a compatible test runner, the `TestWithScenarios` mixin expands `test_demo` into one run per scenario. Each cloned test receives `self.attribute` from the scenario dictionary before the assertion executes.

State and persistence: state is per-test instance attribute injection. No cross-test or persistent state exists.

Dependencies and integration points: depends on `testscenarios.TestWithScenarios` and the scenario expansion machinery in `testscenarios.scenarios` and `testscenarios.testcase`.

Risks and test signals: example assumes the runner honors `TestWithScenarios.run`; overriding `run` incompatibly would bypass multiplication. Test signal is two successful scenario-expanded executions with ids suffixed by `(basic)` and `(advanced)`.
