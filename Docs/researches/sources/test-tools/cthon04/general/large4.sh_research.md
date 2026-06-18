# sources/test-tools/cthon04/general/large4.sh

Purpose: shell workload that compiles four large source files concurrently and removes the resulting executables.

Important APIs/types/functions: uses environment variables CC and CFLAGS, background jobs with &, wait, and rm.

Control flow: launches four compile commands for large.c, large1.c, large2.c, and large3.c in parallel, waits for all background compilers, then removes large, large1, large2, and large3 executables.

State and persistence behavior: transiently creates four executables in the current directory and deletes them at the end. It does not clean object files because direct compile commands do not request separate .o outputs.

Dependencies and integration points: expects the general Makefile to have generated large1.c-large3.c and expects CC/CFLAGS to be set by the surrounding runtests environment.

Risks: no `set -e`, so a failed compiler can be masked by later rm behavior; removes executable names unconditionally; first line is a historical no-op colon before the shebang, so execution depends on invoking it with a shell or permissive systems.

Test signals: the intended signal is that all background compiles finish and the script exits after cleanup; harness timing captures elapsed compile workload.
