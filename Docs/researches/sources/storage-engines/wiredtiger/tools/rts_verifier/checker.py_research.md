# sources/storage-engines/wiredtiger/tools/rts_verifier/checker.py

Purpose: applies semantic checks to parsed rollback-to-stable verbose operations. In current form it is mostly a scaffold: it tracks stable timestamp, current tree, visited trees, and visited pages, while many intended assertions are disabled under PM-3095 comments or TODO placeholders.

Important APIs and control flow: `Checker.apply()` dispatches by `operation.type.name.lower()` to private `__apply_check_*` methods. `__apply_check_init()` resets stable/current state. `__apply_check_tree()` records the current `Tree` and could validate visit necessity and durable/stable comparisons. `__apply_check_tree_logging()` tracks logging state. `__apply_check_page_rollback()` records page address and modified state. `__apply_check_update_abort()`, `__apply_check_page_abort_check()`, and `__apply_check_key_clear_remove()` compute rollback/abort expectations but currently suppress errors. Remaining handlers exist for all parsed RTS operation types and mostly pass.

State and persistence behavior: all state is in-memory and scoped to one checker instance. No output is produced unless a check raises; currently most checks are disabled.

Dependencies and integration points: consumed by `rts_verify.py`, with operation classes from `operation.py` and basic types from `basic_types.py`. It integrates with WiredTiger verbose logging containing `WT_VERB_RTS`.

Risks: because most assertions are commented out, a successful run mostly proves that log lines were parseable, not that RTS behavior was correct. Dispatch through private method naming raises if an operation lacks a handler. Some check methods refer to properties such as `operation.needs_abort` that may not be initialized by the parser for the relevant operation, but disabled code hides the issue.

Test signals: there are no direct unit tests. Meaningful validation would require fixture logs for each operation type and expected pass/fail cases once PM-3095 checks are enabled.
