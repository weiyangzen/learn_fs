<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_nonstandalone.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_nonstandalone.py

Purpose: Marker hook for running the suite in a non-standalone WiredTiger build. It provides a hook name that tests can reference with `skip_for_hook` without changing core behavior.

Important APIs and types: `NonStandAloneHookCreator` extends `wthooks.WiredTigerHookCreator`, returns `wthooks.DefaultPlatformAPI`, has no hook registrations in `setup_hooks`, and `initialize` returns one creator.

Control flow: `run.py --hook nonstandalone` loads the module and installs the creator. The creator does not patch WiredTiger APIs and does not currently register broad skip categories. Individual tests are expected to opt out with decorators or hook-name checks.

State and persistence behavior: No test data, connection config, or persistent file behavior is changed. The only suite-visible state is that `WiredTigerTestCase.hook_names` contains `nonstandalone`.

Dependencies and integration points: Depends on `wthooks` and `wttest`; imported `unittest` and `parse_qsl` are unused. It integrates with `wttest.skip_for_hook`/`runningHook`.

Risks: The method is named `register_skipped_test` rather than the hook-manager-called `register_skipped_tests`, but because no broad skips are needed this has no practical effect unless future logic is added under the wrong name.

Test signals: Tests skipped by explicit nonstandalone decorators and otherwise unchanged suite behavior are the expected signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_nonstandalone.py -->
