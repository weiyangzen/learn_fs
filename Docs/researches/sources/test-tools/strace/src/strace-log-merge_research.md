# sources/test-tools/strace/src/strace-log-merge

Purpose: shell utility that merges per-pid `strace -ff -tt[t]` log files into one timestamp-sorted stream.

Important APIs/types/functions: `show_usage`, `iterate_logfiles`, `process_suffix`, `process_logfile`, timestamp regex variables `dd`/`ds`, `sort`, `sed`, and `grep`.

Control flow: validates one argument or help. It scans `STRACE_LOG.*`, keeps only numeric positive suffixes, first computes the widest suffix for aligned pid prefixes, then emits sortable lines by extracting timestamps and adding the pid suffix. The combined stream is stable-numeric sorted on the synthetic timestamp key, stripped back to original line content with pid prefix, and empty lines removed.

State and persistence behavior: no persistent state; reads matching log files and writes merged output to stdout. Adds an extra newline after each file to tolerate missing final newlines.

Dependencies and integration points: intended for logs produced by `strace -ff -tt`, `-ttt`, or similar timestamp options. Uses POSIX shell plus standard `sed`, `sort`, `grep`, and `printf`.

Risks: timestamp extraction is format-sensitive; logs without expected timestamps yield an error. Numeric suffix filtering ignores non-pid auxiliary files. Sorting by numeric synthetic key can only be as precise as parsed timestamp fields.

Test signals: merge hh:mm:ss, hh:mm:ss.usec, and epoch.usec logs; missing final newline; nonnumeric suffix files; no matching logs; malformed/non-timestamped logs; and equal timestamps requiring stable sort.
