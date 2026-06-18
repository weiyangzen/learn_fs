# sources/user-network-fs/samba/source3/script/samba-log-parser

Purpose: Python 3 diagnostic tool for parsing Samba and especially winbind trace logs by traceid, PID, timestamp, and flow lines.

Important APIs, types, and functions: uses `argparse`, `os.walk`, regexes, `defaultdict` import, and record tuples `(date, traceid, lines, filename)`. Main functions are `process_file_no_traceid`, `process_file`, `filter_traceids`, `filter_flow`, `filter_flowcompact`, `print_record_list`, `setup_parser`, and `main`.

Control flow: argument validation requires one of traceid, pid, breakdown, or merge mode. Files or directories are read into memory. `process_file` groups trace records by header and optionally derives traceids from a client PID. Filtering then either prints merged records, writes per-traceid `.full`, `.flow`, and `.flowcompact` files, or prints filtered flow/full output.

State and persistence: normal modes write to stdout. `--breakdown` creates files named `<traceid>.full`, `<traceid>.flow`, and `<traceid>.flowcompact` in the current directory.

Dependencies and integration: expects Samba non-syslog debug logs with high-resolution timestamps and optionally `winbind debug traceid = yes`.

Risks: reads complete files into memory, which is expensive for large logs. Directory processing order can affect intermediate PID-to-traceid decisions, mitigated by delayed filtering. Breakdown filenames are unsanitized traceid strings from logs/options. UnicodeDecodeError skips files.

Test signals: logs with traceid headers, no-traceid timestamp merge, PID-derived traceids, flow and flow-compact filtering, directory mode, Unicode decode failures, and breakdown file creation.
