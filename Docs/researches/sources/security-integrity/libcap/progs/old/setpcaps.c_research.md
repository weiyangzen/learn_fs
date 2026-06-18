# sources/security-integrity/libcap/progs/old/setpcaps.c

Purpose: legacy example that sets capabilities on running processes using the old `capsetp()` interface.

Important APIs/functions: `read_caps()` reads capability text from stdin when `-` is used. `main()` supports `-q`, parses capability text with `cap_from_text()`, prints the decoded set in debug-disabled builds, parses PID with `atoi()`, and calls `capsetp(pid, cap_d)`.

Control flow: arguments are consumed as repeated capability/PID pairs. Parse or set failures call `usage()`.

State and dependencies: mutates other processes' capabilities when permitted by the kernel and caller's `CAP_SETPCAP` context. Depends on obsolete libcap process APIs.

Risks and test signals: unsafe by design as an example; PID parsing is weak, and modern kernels restrict arbitrary process capability mutation. The usage text states no safe use of `CAP_SETPCAP` had been demonstrated for this pattern.
