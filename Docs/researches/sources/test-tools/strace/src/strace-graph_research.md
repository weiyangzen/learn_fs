# sources/test-tools/strace/src/strace-graph

Purpose: Perl utility that reads `strace -f` output and renders a process tree showing forks/clones/vforks, execs, and approximate elapsed times.

Important APIs/types/functions: global hashes `%unfinished`, `%running_fqname`, `%pr`; parsing helpers `parse_str`, `parse_one`, `parseargs`; trace handlers `handle_trace`, `handle_killed`; display helpers `straight_seq`, `first_exec`, `display_pid_trace`, and `display_trace`.

Control flow: the main loop strips a leading pid, optional timestamps, rejoins unfinished/resumed syscalls, ignores signal and normal-exit marker lines, handles killed markers, parses `call(args) = result` plus optional syscall duration, and passes events to `handle_trace`. `handle_trace` records successful exec argv, child process creation, and exits. `display_trace` climbs to the root parent and recursively prints an ASCII tree with elapsed time divided by a hardcoded slowdown scale.

State and persistence behavior: stores all observed process records in memory until EOF. Tracks running pid-to-qualified-name mapping using `pid-time` to distinguish pid reuse when timestamps exist.

Dependencies and integration points: expects strace text output, preferably with `-f`, `-q`, and sufficient string size. It is a standalone installed helper rather than part of libstrace.

Risks: parser is regex-based and supports only a subset of strace grammar. Complex nested structs, escaped strings, unfinished syscall mismatches, missing timestamps, pid reuse without timestamps, and locale/output format changes can produce warnings or wrong trees. The slowdown scale is fixed.

Test signals: traces with exec, fork/clone/vfork, nested children, unfinished/resumed syscalls, killed processes, timestamped and untimestamped formats, malformed lines, truncated strings, and pid reuse with timestamps.
