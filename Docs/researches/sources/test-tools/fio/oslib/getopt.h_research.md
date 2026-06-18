# sources/test-tools/fio/oslib/getopt.h

Purpose: portable `getopt_long_only()` declaration and `struct option` fallback.

Important APIs/types: when `CONFIG_GETOPT_LONG_ONLY` is set it delegates to system `<getopt.h>`. Otherwise it defines `struct option`, `no_argument`, `required_argument`, `optional_argument`, and declares `getopt_long_only()`.

Control flow and state: header-only compile-time selection.

Dependencies and integration: paired with `getopt_long.c`; used by fio command-line parsing on platforms without GNU getopt extensions.

Risks: fallback intentionally implements only a common subset, so code must not depend on unsupported GNU features.

Test signals: CLI option parsing tests on systems with and without native `getopt_long_only()`.
