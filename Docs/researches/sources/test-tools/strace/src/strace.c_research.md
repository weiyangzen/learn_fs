# sources/test-tools/strace/src/strace.c

Purpose: main `strace` executable driver. It parses command-line options, starts or attaches tracees, manages `struct tcb` lifetime, runs the ptrace wait/restart event loop, owns shared/per-PID output streams, and terminates with cleanup, summaries, and optional tips.

Important APIs/types/functions: global flags such as `cflag`, `followfork`, `output_separately`, `ptrace_setoptions`, timestamp flags, `outfname`, `shared_log`, `printing_tcp`, `current_tcp`, `tcbtab`, and `tcb_wait_tab` are the process-wide tracing state. Core functions include `init`, `startup_child`, `startup_attach`, `attach_tcb`, `after_successful_attach`, `alloctcb`, `droptcb`, `printleader`, `next_event`, `dispatch_event`, `trace_syscall`, `cleanup`, and `terminate`. `struct tcb_wait_data` carries a `trace_event`, wait status, ptrace event message, and signal info between wait collection and dispatch.

Control flow: `main` localizes, calls `init`, then loops over `dispatch_event(next_event())`. Initialization sets defaults, parses short/long options, configures qualifiers, ptrace options, output files, signal handling, seccomp, stack tracing, user credentials, path filters, and starts a command or attaches requested PIDs. `next_event` batches `wait4(__WALL)` results into per-TCB wait records, classifies them as syscall, signal, exit, exec, seccomp, group-stop, or restart events, and queues multiple events safely. `dispatch_event` decodes syscalls through `syscall.c`, prints signal/exit/exec messages, handles seccomp stop ordering, delayed injection timers, and restarts tracees with `PTRACE_SYSCALL`, `PTRACE_CONT`, `PTRACE_LISTEN`, or detach.

State and persistence behavior: state is in process memory plus output files or pipe commands. TCBs persist while tracees are live; per-TCB private data, inject vectors, unwind/KVM/mmap caches, delayed wait data, and staged memstreams are released on drop or syscall exit. Output can be shared, per-PID, appended, or piped. No repo data is persisted.

Dependencies and integration points: depends on ptrace, wait, procfs, seccomp filtering, signal and timer handling, output/color helpers, number-set qualifiers, path tracing, SELinux context printing, stack unwind, mmap cache, syscall decoding (`syscall.c`), and `trace_event.h`.

Risks: ptrace stop ordering, disappearing tracees, exec PID switches, NOMMU/vfork paths, seccomp kernel-version differences, partial output lines, attached process permissions, setuid UID swaps, and delayed injection restarts are high-risk. Output filtering relies on memstream support. Signal cleanup must avoid leaving attached processes stopped.

Test signals: exercise starting a command, `-p` attach with threads, `-f/-ff`, `-D/-DD/-DDD`, `-b execve`, status filters, `--seccomp-bpf`, `--syscall-limit`, output pipes/files, signal interruption, stopped tracees, threaded execve PID switching, delayed injection, and summary modes.
