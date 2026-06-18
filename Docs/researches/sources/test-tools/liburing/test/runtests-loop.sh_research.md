# sources/test-tools/liburing/test/runtests-loop.sh

Purpose: simple stress harness that repeatedly invokes `./runtests.sh` with the user-supplied test list until a run fails.

Important APIs/types/functions: Bash arrays, infinite `while true` loop, command status `$?`, integer iteration counter, and pass-through arguments.

Control flow: captures `"$@"` into `TESTS`, runs `./runtests.sh "${TESTS[@]}"`, breaks and reports the loop index on nonzero exit, otherwise prints completion and increments `ITER`.

State/persistence behavior: no private persistent state beyond stdout and whatever `runtests.sh` writes, such as output timings or failure artifacts. The loop counter is process-local.

Dependencies/integration: assumes current working directory contains executable `runtests.sh` and built test binaries. It is a wrapper around the main liburing test harness.

Risks/test signals: failures are surfaced only when `runtests.sh` returns nonzero. The loop is intentionally unbounded and needs external termination for long soak runs.
