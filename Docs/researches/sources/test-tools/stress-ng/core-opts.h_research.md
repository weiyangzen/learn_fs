# sources/test-tools/stress-ng/core-opts.h

Purpose: defines global option flag bits and the complete command option enum namespace.

Important APIs/types: `OPT_FLAGS_*` bit masks, `OPT_FLAGS_MINMAX_MASK`, `OPT_FLAGS_AGGRESSIVE_MASK`, declaration of `stress_long_options`, and the `stress_op_t` enum covering short options and long-only IDs.

Control flow: no runtime flow. Enum values form the dispatch contract consumed by command-line parsing and stressor option tables.

State/persistence: no direct state, but flag bits are stored in global `g_opt_flags` elsewhere.

Dependencies/integration: includes `<unistd.h>` and `<getopt.h>`, relies on `STRESS_BIT_ULL`, and must align with `core-opts.c`, parser switch logic, stressor option tables, and help generation.

Risks: only 64 global flag bits are available; enum churn can break switch cases; conditional options still need enum IDs here; this is a large manual registry with typo/duplication risk.

Test signals: compile all stressor option tables, run registry consistency checks, exercise short aliases, and validate global flags through CLI integration tests.
