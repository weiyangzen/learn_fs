## sources/security-integrity/libcap/libcap/cap_text.c

Purpose: parses and renders textual capability and IAB formats, maps names to numeric values, reports mode names, manages proc-root override, and reads IAB from `/proc/<pid>/status`.

Important APIs/functions: `cap_from_text`, `cap_to_text`, `cap_from_name`, `cap_to_name`, `cap_mode_name`, `cap_iab_to_text`, `cap_iab_from_text`, `cap_proc_root`, `cap_iab_get_pid`, plus helpers `lookupname`, `forceall`, `_parse_vec_string`.

Control flow: text parser tokenizes capability clauses with `all`, named or numeric values and `+/-/=` operations over e/i/p flags. Renderer builds a compact canonical form by histogramming state combinations and naming deviations. IAB text uses prefixes `!` for bounding drops, `^` for ambient+inheritable, and `%` for inheritable with bounding. `/proc` IAB reader parses `CapInh`, `CapBnd`, and `CapAmb` hex vectors from status, inverting bounding to libcap's drop-bit representation.

State/persistence: allocates returned strings/IAB/cap sets; process-global `_cap_proc_dir` controls proc root and is cleaned by destructor.

Dependencies/integration: generated `cap_names.h`, optional gperf output, `/proc`, public text ABI used by capsh, Go compatibility, and docs.

Risks: parser is compact and format-sensitive; global proc root setter is documented not thread-safe; `cap_to_name` returns numeric strings for unknown values.

Test signals: `cap_test` buffer/name assumptions, Go `compare-cap` text round trips, capsh text parsing tests, and `/proc` fixture tests for `cap_iab_get_pid`.
