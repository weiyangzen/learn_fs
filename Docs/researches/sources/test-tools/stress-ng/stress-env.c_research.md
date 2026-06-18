# sources/test-tools/stress-ng/stress-env.c

Purpose: implements the `env` stressor, repeatedly creating, verifying, and removing environment variables with randomized names and randomized value lengths up to the platform argument/environment limit.

Important APIs/types/functions: `stress_env_size()` chooses a random value length, `stress_env_max()` chooses how many variables to create before a reap cycle, and `stress_env_child()` owns allocation, random value generation, set/get/unset loops, optional verification, and cleanup. `stress_env()` runs the child through `stress_oomable_child()`.

Control flow: the child derives `arg_max` from `_SC_ARG_MAX`, `ARG_MAX`, or `NCARGS`, caps it at 16 MiB, mmaps a value buffer, fills it with random text, then sync-starts. It repeatedly builds names `STRESS_ENV_<hex>`, temporarily null-terminates the buffer at a random offset, calls `setenv()`, and increments bogo operations. When the selected limit is reached or `setenv()` fails, it reseeds to replay the same lengths, optionally compares `getenv()` values, calls `unsetenv()`, and begins a new cycle.

State and persistence behavior: state lives in the process environment and an anonymous mmap buffer. Environment mutations are local to the worker child and are removed during each reap pass; no filesystem state is created. Low-memory checks deliberately terminate the child cleanly so the OOM wrapper can manage pressure.

Dependencies and integration points: uses stress-ng random, memory, OOM-child, killpid, sync, process-state, and verification flag helpers. The stressor is registered as `CLASS_OS | CLASS_VM` with optional verification.

Risks: very large environment values can exhaust memory or hit platform-specific `ARG_MAX` behavior. Verification depends on replaying the RNG seed sequence exactly across set and unset passes. Early stop can leave variables in the exiting child, but they disappear with the process.

Test signals: run with `--env 1 --verify`, minimized/maximized modes, low memory pressure, and varied libc/kernel argument limits; check for skip messages on mmap failure and for missing/incorrect variable failures only under real corruption.
