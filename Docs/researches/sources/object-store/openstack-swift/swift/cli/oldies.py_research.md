# sources/object-store/openstack-swift/swift/cli/oldies.py

Purpose: lists old Swift daemon processes, optionally as PIDs only for piping to tools like `xargs kill`.

Important APIs: `main()` parses `--age` and `--pids`, runs `ps -eo etime,pid,args --no-headers`, filters known Python Swift executable prefixes, parses elapsed time into hours, and formats output.

Control flow: each process line is ASCII-decoded and split into elapsed time, pid, and args. Non-Swift command prefixes are skipped. Elapsed times with days add `days * 24`; `HH:MM:SS` adds hours; `MM:SS` adds no hours. Processes at or above the threshold are collected and printed as either PIDs or aligned table rows.

State and persistence: read-only process inspection; no signals are sent.

Dependencies and integration: depends on Linux `ps` output format and installed Swift command paths.

Risks: prefix matching is narrow and may miss venv, alternate install paths, or non-CPython launchers. It exits on unexpected parse formats. Tests should mock `subprocess.Popen` output for day/hour formats, prefix filtering, PIDs-only output, no matches, and malformed lines.
