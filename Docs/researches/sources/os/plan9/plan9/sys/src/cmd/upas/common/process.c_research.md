# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/process.c

- Role: Child process and pipe stream management for upas tools.
- Key functions: `instream`, `outstream`, `stream_free`, `noshell_proc_start`, `proc_start`, `proc_wait`, `proc_free`, and `proc_kill`.
- Behavior: Creates Bio-backed pipes, forks, dup’s requested standard fds, optionally detaches and calls `become`, then execs.
- Risks/notes: Error paths after pipe/Binit allocation can leak partially allocated stream memory.
