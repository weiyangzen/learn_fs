# sources/sync-backup/borg/src/borg/testsuite/helpers/msgpack_test.py

Purpose: verifies detection of slow pure-Python msgpack fallback while skipping environments where slow msgpack is expected.

Important APIs and control flow: `expected_py_mp_slow_combination` imports upstream `msgpack`, returns true for Cygwin and Python 3.12 with msgpack older than 1.0.6, and is used as a skip condition. The test temporarily replaces `msgpack.Packer` with `msgpack.fallback.Packer` to require `is_slow_msgpack()`, then restores it and requires fast detection.

State and persistence: mutates the imported `msgpack.Packer` symbol in-process and restores it in `finally`.

Dependencies and integration points: depends on upstream msgpack internals, Borg `helpers.msgpack.is_slow_msgpack`, Python version, and Cygwin platform flag. Borg warns or adapts based on msgpack performance.

Risks: relies on upstream `msgpack.fallback.Packer` existing and on wheel availability assumptions. Failing to restore `msgpack.Packer` would leak process-global state, but the test uses `finally`.

Test signals: slow detection under forced fallback and fast detection under the real packer.
