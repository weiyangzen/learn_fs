# sources/test-tools/stress-ng/core-signal.c

Purpose: provides signal name formatting, generic handler installation/restoration, stop/exit handlers, longjump masking, SIGCHLD handling, and diagnostic SIGILL/SIGSEGV catchers.

Important APIs/types/functions: `stress_signal_name`, `stress_signal_str`, `stress_signal_longjump_mask`, `stress_signal_handler`, `stress_signal_sigchld_handler`, `stress_signal_default_handler`, `stress_signal_stop_stressing`, `stress_signal_restore`, `stress_signal_alrm_pending`, `stress_signal_exit_handler`, `stress_signal_ignore_handler`, `stress_signal_stop_flag_handler`, `stress_signal_catch_sigill`, and `stress_signal_catch_sigsegv`.

Control flow: name lookup checks realtime signal ranges then a static table. The generic handler lazily allocates one alternate signal stack with `stress_mmap_populate`, names it, installs it with `stress_stack_sigalt`, builds a `sigaction`, masks longjump-capable fatal signals for termination signals, sets `SA_NOCLDSTOP` and optionally `SA_ONSTACK`, then calls `sigaction`. Stop handlers clear the global continue flag and for alarms re-arm another alarm until workers notice. SIGCHLD handler finds args for the current PID and stops bogo counting. Diagnostic catchers use `SA_SIGINFO`, guard against recursion, print signal/address/si_code, dump nearby readable bytes, locate the mapping in `/proc/self/maps`, and `_exit(EXIT_FAILURE)`.

State and persistence: static signal-name buffers and the lazily allocated alt stack persist for process lifetime; comments acknowledge the stack leak. Installed handlers persist until restored or process exit.

Dependencies/integration: uses mmap, stack, memory-readable, logging, `stress_args_pid_find`, bogo-stop, continue flags, and Linux `/proc/self/maps` when available.

Risks: some diagnostic helpers use formatting and writes in signal context; they try to keep buffers small but are not purely async-signal-safe. The generic alt-stack allocation is process-global and leaked intentionally. `stress_signal_str` uses a static buffer, so concurrent calls overwrite it.

Test signals: install/restore handlers, pending ALRM detection, stop flag behavior, SIGCHLD helper, SIGILL/SIGSEGV diagnostics in child processes, and builds without `sigaltstack` or `/proc`.
