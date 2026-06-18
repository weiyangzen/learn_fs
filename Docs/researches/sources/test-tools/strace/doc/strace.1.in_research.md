# sources/test-tools/strace/doc/strace.1.in

Purpose: canonical roff source for the `strace(1)` manual page. It documents the command synopsis, event trace format, option grammar, filtering, output controls, statistics, tampering, diagnostics, ABI/personality support, caveats, history, and reporting channels. Autoconf substitutions such as `@VERSION@`, `@STRACE_MANPAGE_DATE@`, `@ENABLE_STACKTRACE_FALSE@`, and `@ENABLE_SECONTEXT_FALSE@` make parts of the manual conditional on build features.

Important APIs/types/functions: this file is not executable code, but it defines user-visible contracts for CLI options including `-e` qualifiers, `--trace`, `--trace-fds`, `--status`, `--decode-fds`, `--decode-pids`, `--inject`, `--fault`, `--seccomp-bpf`, `--syscall-limit`, timestamp options, summary columns, stack traces, SELinux contexts, and tip output. It also defines local roff macros `CW`, `CE`, `OM`, and `OR` for code blocks and option formatting.

Control flow: the document progresses from synopsis and conceptual trace examples into option families: startup, tracing, filtering, output format, statistics, tampering, and miscellaneous behavior. Later sections describe exit status behavior, setuid installation, multiple personalities, notes, bugs, history, reporting, and related tools. Conditional roff lines include or omit feature-specific text during configure-time rendering.

State and persistence behavior: documents how `strace` observes live tracee state at syscall entry/exit, dereferences pointers only when safe and relevant, tracks unfinished/resumed calls, can alter tracee behavior with injection/poking/delays, can write one log or per-PID logs, and can leave or kill tracees depending on detach/exit settings.

Dependencies and integration points: integrates with the build system via substitution tokens and with implementation files that parse options, maintain qualifier sets, decode syscalls, collect summaries, implement seccomp filtering, and support mpers ABI decoding. It also references external Linux APIs such as `ptrace(2)`, `seccomp(2)`, signals, namespaces, SELinux, and process credentials.

Risks: because this is the public contract, drift from actual option parsing or decoder behavior is high impact. Conditional feature guards must remain aligned with configure variables. Examples and lists such as syscall classes, summary columns, color keys, and injection syntax are regression-prone when implementation evolves.

Test signals: generated manpage checks, `strace -h`, `strace -V`, CLI option tests, documentation spelling/style checks, and behavior tests for filters, output formatting, seccomp, injection, and mpers should confirm that documented syntax and defaults match the binary.
