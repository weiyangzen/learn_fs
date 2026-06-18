# sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke.sh

Purpose: standard smoke wrapper for `test_random_abort`.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, optional binary path argument, `binary_dir` fallback, `TEST_WRAPPER`, and fixed test options.

Control flow: resolves `test_random_abort`, then runs four variants: default logged disk mode, in-memory logging (`-m`), compatibility mode (`-C`), and compatibility plus in-memory logging. Every variant uses `-t 10 -T 5` to bound runtime and thread count.

State and persistence behavior: the wrapper writes no direct state. Each binary invocation creates and cleans its own random-abort work directory unless failure/preserve options intervene.

Dependencies and integration points: registered as `EXEC_SCRIPT` for `test_random_abort`; `CMakeLists.txt` also lists the LazyFS companion script as an additional file. Depends on `TEST_WRAPPER` and POSIX shell behavior.

Risks: four sequential crash/recovery runs can be expensive on slow machines. The script does not run compaction or LazyFS variants; those are covered separately.

Test signals: zero exit from all four fixed variants is the smoke signal for recovery under default, in-memory log buffering, compatibility, and combined modes.
