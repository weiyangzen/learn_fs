<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/wthooks.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/wthooks.py

Purpose: Generic hook framework for the WiredTiger Python suite. It loads hook modules, monkey-patches WiredTiger module/class methods, chains argument/notification hooks, supports one replacement hook per method, and exposes platform APIs to the test harness.

Important APIs and types: Constants `HOOK_REPLACE`, `HOOK_NOTIFY`, `HOOK_ARGS`; `WiredTigerHookInfo`; `hooked_function`; `WiredTigerHookManager`; `HookCreatorProxy`; abstract `WiredTigerHookCreator`; `DisaggParameters`; `WiredTigerHookPlatformAPI`; `DefaultPlatformAPI`; and `MultiPlatformAPI`.

Control flow: `WiredTigerHookManager` parses hook names and optional args, imports `hook_<name>`, calls `initialize`, initializes each creator with proxies, calls `setup_hooks`, collects platform APIs, and appends the default API. `add_hook` installs a wrapper the first time a class/method is hooked, stores the original method, and appends arg/notify functions or records a single replacement. `hooked_function` runs arg hooks, calls replacement or original, then notifies hooks.

State and persistence behavior: Hook metadata is stored as new attributes on the WiredTiger module/classes, such as `_<method>_hooks` and `_<method>_orig`. This is process-global monkey-patched state and persists for the Python process. Platform APIs are chained in manager order and fall back to `DefaultPlatformAPI`.

Dependencies and integration points: Uses Python import machinery, `wiredtiger` bindings, `WiredTigerTestCase` for debug tty, and hook modules like tiered/disagg/timestamp. `wttest` calls `get_platform_api`, `register_skipped_tests`, `get_hook_names`, and `hooks_using`.

Risks: Only one replacement hook per method is allowed, so hook combinations can conflict. Method signature mismatches surface at runtime. Process-global patches are not undone between suites. `MultiPlatformAPI` uses first non-`NotImplementedError` result, making ordering significant.

Test signals: Hooks are validated indirectly by command-line hook runs, expected skip registration, modified connection configs, platform API overrides, and absence of duplicate replacement errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/wthooks.py -->
