# sources/user-network-fs/nfs-ganesha/src/tools/findlog.sh

Purpose: shell utility to extract multiline function calls, primarily `Log...` calls, from C source and normalize each call onto one output line with file and line number.

Important APIs, types, and functions: configurable variables include `FUNC`, `PRINTF`, `FILES`, `TODO`, `CSCOPE`, `FINAL`, `LINESONLY`, and `DIR`. Functions include `find_funcs`, `debug_mode`, `no_xref`, `final_massage`, `final_lines_only`, `find_func_in_file`, and `find_files`.

Control flow: option parsing selects function regex, file list, cscope mode, printf mode, debug/no-xref/line-only modes, and search directory. Non-cscope mode reads file names either from a list, arguments, or `find $DIR -name '*.[ch]'`, then feeds each through sed logic that joins multiline calls until terminators. Cscope mode shells out to `cscope -d -L -0`.

State and persistence: no persistent state; output is stdout. It reads source files and optional file lists.

Dependencies and integration points: depends on POSIX shell, sed, grep, find, cat, and optionally cscope. `tools/test_findlog.c` is referenced as a behavior corpus.

Risks: many expansions are unquoted, so paths with spaces break. The sed parser is intentionally heuristic and can be confused by macros, comments, nested syntax, or function names without preceding blank/tab. Cscope mode hardcodes `Log.*` extraction in sed even when `FUNC` is changed.

Test signals: use `tools/test_findlog.c` plus representative source files to compare expected output, line-only output, no-xref output, and cscope parity.
