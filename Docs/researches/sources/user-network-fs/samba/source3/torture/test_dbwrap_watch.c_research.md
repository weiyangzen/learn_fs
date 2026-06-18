# sources/user-network-fs/samba/source3/torture/test_dbwrap_watch.c

Purpose: This file tests the watched dbwrap API: keyed watch notification, invalid watched-record data handling, cleanup of dead watchers, and rejection of duplicate watches in one locked update round.

Important APIs/types/functions: `test_dbwrap_watch_init()` creates a tevent context, messaging context, TDB backend, and watched wrapper via `db_open_watched()`. `run_dbwrap_watch1()` uses `dbwrap_fetch_locked()` and `dbwrap_watched_watch_send()`. `run_dbwrap_watch2()` writes invalid watcher metadata directly to the backend. `run_dbwrap_watch3()` forks a child that registers a watch then exits. `run_dbwrap_watch4()` uses `dbwrap_do_locked()` and two watch requests to verify duplicate rejection.

Control flow: The first test watches key `"key"`, stores a different key to prove no completion, stores the watched key, polls the request, and expects success. The second test stores `UINT32_MAX` directly in the backend and expects the watched wrapper to treat it as not found. The third test waits for a child watcher process to exit, then stores the watched key and expects dead watcher cleanup not to fail. The fourth test creates two watches within one locked callback, stores the key, drains the event loop, and expects the first request OK and the second `NT_STATUS_REQUEST_NOT_ACCEPTED`.

State/persistence behavior: All tests use `test_watch.tdb` and unlink it on success paths. Persistent state includes regular records plus watched-db metadata used to resume or notify watchers. Process liveness matters because dead watcher records must be cleaned when a store occurs.

Dependencies and integration points: The file depends on tevent, messaging, dbwrap open APIs, watched dbwrap, TDB utilities, fork/wait behavior, and NTSTATUS request lifecycles. It covers a core integration point between dbwrap record updates and Samba interprocess messaging.

Risks: Forked watcher cleanup is timing and platform sensitive. Some failure paths do not unlink the test database before returning, which can affect later manual runs. Duplicate-watch semantics are subtle because both requests are created in one locked record callback and endtimes are used to avoid indefinite waits.

Test signals: Key success signals are watch completion after the target key changes, `NT_STATUS_NOT_FOUND` for invalid backend watcher data, successful store after a dead child watcher exits, and `NT_STATUS_REQUEST_NOT_ACCEPTED` for the second same-round watch.
