# sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke_lazyfs.sh

Purpose: LazyFS-specific smoke wrapper for `test_random_abort`.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, optional binary argument, build-directory fallback, `TEST_WRAPPER`, and the binary's `-l` LazyFS flag.

Control flow: resolves `test_random_abort`, then runs LazyFS mode with `-l -t 30 -T 5` and LazyFS plus compatibility mode with `-l -C -t 30 -T 5`.

State and persistence behavior: no direct script state. The binary creates the LazyFS work directory, sets up/cleans LazyFS, and clears the LazyFS cache before recovery verification.

Dependencies and integration points: listed as `ADDITIONAL_FILES` for the random-abort CMake target. It assumes the environment has LazyFS support; the binary can implicitly enable LazyFS as well.

Risks: longer timeout than the standard smoke script increases runtime. LazyFS availability and mount/setup behavior are environment-sensitive.

Test signals: zero exit from both LazyFS variants validates recovery under simulated lost write-cache behavior.
