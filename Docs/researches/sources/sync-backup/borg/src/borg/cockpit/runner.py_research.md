# sources/sync-backup/borg/src/borg/cockpit/runner.py

Purpose: wraps asynchronous execution of a Borg subprocess and reports decoded stdout/stderr lines plus final return code to a callback.

Important APIs: `BorgRunner(command, log_callback)` stores the command list and callback. `start()` prevents double starts, builds either `[sys.executable] + command` for frozen binaries or `[sys.executable, "-m", "borg"] + command` for source execution, sets `PYTHONUNBUFFERED=1`, starts the subprocess with stdout/stderr pipes, reads both streams concurrently, emits `{"type": "stream_line", "stream": ..., "line": ...}`, waits for the process, then emits `{"type": "process_finished", "rc": rc}`. Exceptions produce `rc=-1`. `stop()` terminates a running process and waits.

Control flow and state: `self.process` is non-`None` while active and reset in `finally`. The nested `read_stream` coroutine runs until EOF. `stop()` only terminates processes with no return code.

Dependencies and integration: uses `asyncio.create_subprocess_exec`, Python runtime path, environment copy, and a UI callback supplied by `BorgCockpitApp`.

Risks: subprocess termination has no timeout or kill escalation after `terminate()`. Very long lines are read as complete lines, so memory use depends on subprocess output behavior. All stderr/stdout lines are treated equally by the app except for the `stream` field.

Test signals: cover source and frozen command construction, callback events for stdout/stderr and return code, exception path with `rc=-1`, double-start warning/no-op, and stop behavior for live and already-dead processes.
