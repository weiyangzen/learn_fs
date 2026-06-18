# sources/security-integrity/audit-userspace/audisp/test/test-audispd-llist.c

Purpose: Exercises audisp plugin linked-list behavior as used by audispd configuration management, HUP reload reconciliation, startup iteration, and edge-case cleanup.

Important APIs, types, and functions: Uses `conf_llist`, `lnode`, `plugin_conf_t`, `active_t`, and list APIs from `audispd-llist.h`: `plist_create()`, `plist_append()`, `plist_count()`, `plist_count_active()`, `plist_find_name()`, `plist_mark_all_unchecked()`, `plist_find_unchecked()`, `plist_first()`, `plist_next()`, `plist_get_cur()`, `plist_last()`, and `plist_clear()`. Helpers create and free test plugin configs.

Control flow: The file defines a simple macro-based test runner. `test_plugin_configuration_management()` validates append, counts, name lookup, unchecked marking, iteration, and clearing. `test_plugin_hup_signal_handling()` simulates old/new plugin lists during SIGHUP reload: mark old unchecked, match new names, update active state, append new plugins, and identify removed plugins. `test_plugin_iteration_and_startup()` walks mixed active/inactive plugins and simulates assigning PIDs to active entries. `test_memory_management_and_edge_cases()` covers empty operations, NULL plugin append, repeated clear, a 1000-node list, lookup, and active counts. `main()` runs all tests and returns failure if any test did not call `TEST_PASS()`.

State and persistence: All state is process-local test heap data. The linked list stores copies or references according to the implementation under test; the harness frees its original configs after `plist_clear()`, implying `plist_append()` must not leave ownership ambiguity that double-frees caller-owned memory.

Dependencies and integration points: Links against `libdisp.la`, which contains the real audisp linked-list implementation and plugin config helpers. The scenarios are explicitly modeled after audispd's plugin startup and reload logic.

Risks and edge cases: The test expects `plist_append(NULL)` to succeed and create a node with NULL plugin data. It also assumes large list operations remain O(n) but functional. Because it validates behavior through public list APIs, it is less brittle than direct source inclusion tests, though it does not simulate process management or actual plugin child lifecycles.

Test signals: Built as `audisp-llist-test`. Passing signals that plugin list management can support HUP reconciliation, active counting, startup iteration, empty list operations, and repeated cleanup without obvious memory or cursor failures.
