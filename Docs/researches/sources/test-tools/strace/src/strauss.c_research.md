# sources/test-tools/strace/src/strauss.c

Purpose: implements the optional Strauss mascot and "tip of the day" output used by version/help-adjacent paths and process exit.

Important APIs/types/functions: `strauss[]`, `strauss_lines`, `tips_tricks_tweaks`, `show_tips`, `tip_id`, `print_strauss`, and `print_totd`. Constants in `strauss.h` define verbosity threshold, formatting modes, and random-tip selection.

Control flow: `print_strauss` only prints art when version verbosity reaches `STRAUSS_START_VERBOSITY`, then bounds the number of lines by `strauss_lines`. `print_totd` is idempotent through a static `printed` guard, chooses a tip by configured ID or pseudo-random `gettimeofday` seed, formats a speech bubble, and optionally prints full mascot art.

State and persistence behavior: global `show_tips` and `tip_id` are configured by option parsing in `strace.c`; `print_totd` uses only in-process static state and writes to stderr. No persistent state.

Dependencies and integration points: depends on `defs.h`, `strauss.h`, libc random/time APIs, and `strace.c` option parsing/termination.

Risks: formatting assumes fixed ASCII art widths and non-null tip rows. Random selection is intentionally non-cryptographic. Repeated calls are suppressed, so tests must reset process state.

Test signals: cover no-tip mode, compact/full tips, explicit ID modulo tip count, random ID path, version verbosity below/above threshold, and multiple `print_totd` calls.
