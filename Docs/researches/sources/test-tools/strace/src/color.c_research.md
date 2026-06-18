<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/color.c -->
## sources/test-tools/strace/src/color.c

Purpose: Initializes optional ANSI color output for strace formatting.

Important APIs and types: Globals `color_is_enabled`, `color_mode`, `color_seq_table`; local `struct color_key`; helpers `lookup_color_kind`, `trim_spaces`, `is_sgr_seq`, `make_sgr_seq`, `parse_strace_colors`, `is_no_color`; exported `color_init`.

Control flow: `color_init` disables color by default, exits for `COLOR_NEVER`, evaluates tty/output-separately/NO_COLOR/TERM for `COLOR_AUTO`, initializes the sequence table from defaults, parses `STRACE_COLORS` overrides, then sets `color_is_enabled`. The parser accepts colon-separated `name=sgr` entries and ignores unknown or invalid pieces.

State and persistence: Global color mode and sequence table persist for the process. Custom SGR sequences are heap-allocated by `xasprintf`; replacement frees any prior non-default sequence for that kind.

Dependencies and integration: Depends on `defs.h`, `color.h`, libc string/ctype APIs, optional termcap `tgetent`/`tgetnum`, environment variables `NO_COLOR`, `TERM`, and `STRACE_COLORS`.

Risks: `trim_spaces` computes `strlen(s) - 1`, so empty strings after leading trim need careful reasoning; current parser calls it on token fragments that can be empty. Invalid SGR data is ignored silently. Color escapes must be emitted via uncolored output paths to avoid recursive styling.

Test signals: Tests should cover auto/never/always modes, non-tty and per-pid output, `NO_COLOR`, `TERM=dumb`, valid and invalid `STRACE_COLORS`, case-insensitive keys, and duplicate overrides.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/color.c -->
