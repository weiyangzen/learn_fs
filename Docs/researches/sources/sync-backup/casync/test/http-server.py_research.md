# sources/sync-backup/casync/test/http-server.py

Purpose: starts a small HTTP server rooted at a supplied directory for remoting integration tests.

Important APIs/types/functions: parses directory and port arguments, changes/serves the requested root, sends readiness notification, and runs Python's HTTP server loop.

Control flow/state: process-level current directory and socket listener are the main state. Once ready, it stays foreground until killed by the test script.

Dependencies/integration: launched through `notify-wait` by `test-script.sh.in` to serve `.caidx` and `.catar` files over `http://localhost:PORT`.

Risks/test signals: port collisions, Python version differences, and cwd mutation are the main risks. The HTTP remoting section of `test-script.sh.in` validates it.

Source research group: `subset-b-009122`.
