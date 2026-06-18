<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_demo.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_demo.py

Purpose: Demonstration hook showing how the WiredTiger Python test hook framework can alter open arguments, observe API results, and replace session methods.

Important APIs and types: Hook functions include `wiredtiger_open_args`, `wiredtiger_open_notify`, `session_open_cursor_notify`, and `session_create_replace`. `DemoHookCreator` extends `wthooks.WiredTigerHookCreator`, and `initialize` returns a creator instance.

Control flow: `setup_hooks` retrieves the original `Session.create`, registers an argument hook on `wiredtiger_open` to append cache size, a notify hook after `wiredtiger_open`, a replacement hook for `Session.create`, and a notify hook on `Session.open_cursor`. The replacement create behavior depends on the numeric hook argument: normal create, create then drop, or create/drop/create.

State and persistence behavior: Mode 1 deliberately removes newly created objects; mode 2 recreates them. Debug messages go to `/dev/tty` via `WiredTigerTestCase.tty` to avoid polluting captured stdout/stderr.

Dependencies and integration points: Exercises `wthooks` hook registration and the global monkey-patched WiredTiger bindings. It is launched by `run.py --hook demo=N` and uses `WiredTigerTestCase` only for debug output.

Risks: It is intentionally disruptive in some modes and can make normal tests fail. It demonstrates that replacement hooks must preserve original method signatures and that multiple assignments to one method add hook behavior rather than replace prior hook metadata.

Test signals: The signal is behavioral: hook debug output on the terminal and expected pass/fail behavior depending on the mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_demo.py -->
