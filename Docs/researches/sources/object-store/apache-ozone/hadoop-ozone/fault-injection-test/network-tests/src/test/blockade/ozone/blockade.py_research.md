## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/blockade.py

Purpose: Python wrapper around the external `blockade` CLI used by Ozone network fault-injection tests. It centralizes cluster lifecycle and network partition commands so tests and `OzoneCluster` do not shell out directly.

Important APIs/types/functions: `Blockade.blockade_destroy`, `blockade_up`, `blockade_status`, `make_flaky`, `blockade_fast_all`, `blockade_create_partition`, `blockade_join`, `blockade_stop`, `blockade_start`, and `blockade_add`. All are classmethods. Most use `subprocess.call`; `blockade_create_partition` uses `ozone.util.run_command` to assemble variadic partition sets into a single command string.

Control flow: callers first check/destroy an existing blockade state, run `blockade up`, add docker-compose containers, then use partition/fast/join/stop/start helpers during tests. Failures are surfaced by assertions on exit codes for mutating operations.

State and persistence behavior: no Python-local persistent state. State lives in blockade/docker networking and container runtime. `blockade_create_partition` builds a space-delimited list of comma-joined node groups that blockade interprets as separate network partitions.

Dependencies and integration points: depends on `blockade` being installed and on `ozone.util.run_command`. Integrated by `ozone.cluster.OzoneCluster` and `test_blockade_flaky.py`.

Risks: asserts can be optimized away with Python `-O`; command construction is string-based; `import util` is package-relative fragile; there is no timeout around blockade calls.

Test signals: exercised indirectly by all blockade tests that create partitions, restore networks, or mark nodes flaky.
