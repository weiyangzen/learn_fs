# sources/storage-engines/wiredtiger/test/3rdparty/testscenarios-0.4/lib/testscenarios/scenarios.py

Purpose: core scenario expansion functions for `testscenarios`. It clones tests and injects parameter dictionaries so the same test logic can run against multiple implementations or configurations.

Important APIs, types, and functions: `apply_scenario()` clones a test with `clone_test_with_new_id`, appends `(scenario-name)` to the id, adjusts `shortDescription`, and sets attributes from the scenario parameter dict. `apply_scenarios()` yields one adapted test per scenario. `generate_scenarios()` walks suites with `testtools.iterate_tests`, expands tests with a truthy `scenarios` attribute, and clears `newtest.scenarios`. `load_tests_apply_scenarios()` supports both Python 2.7 and bzr-style `load_tests` call conventions. `multiply_scenarios()` returns cross-product scenario tuples. `per_module_scenarios()` imports implementation modules or stores `sys.exc_info()` when import fails.

Control flow: test suites are flattened, tests with scenarios are replaced by generated clones, and tests without scenarios pass through unchanged. Multiplication materializes input iterables into lists, iterates `itertools.product`, concatenates names, and merges parameter dictionaries left to right.

State and persistence: state is confined to cloned test instances and scenario lists. `per_module_scenarios()` may import modules and therefore populate `sys.modules`; no disk state is changed.

Dependencies and integration points: depends on `itertools`, `sys`, `unittest`, `testtools.iterate_tests`, and `testtools.testcase.clone_test_with_new_id`. It integrates with unittest `load_tests` and the `WithScenarios` mixin.

Risks and test signals: `except:` in `per_module_scenarios()` captures all import failures, including unexpected initialization failures, and represents them as scenario data. Parameter key collisions in `multiply_scenarios()` are silently resolved by later dictionaries. Tests in `test_scenarios.py` cover id suffixes, attribute injection, old/new `load_tests` signatures, cross-product generation, and missing-module scenarios.
