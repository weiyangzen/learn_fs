# sources/security-integrity/audit-userspace/rules/42-injection.rules

Purpose: detects ptrace tracing and injection-like operations.

Important rules: active b64 broad `ptrace` tracing rule, plus b32/b64 argument-specific rules for `PTRACE_POKETEXT`, `PTRACE_POKEDATA`, and `PTRACE_POKEUSER` style values with keys `code-injection`, `data-injection`, and `register-injection`.

Control flow: syscall exit filters with argument equality.

State and persistence: kernel audit rules.

Dependencies and integration: parsed through syscall and argument field support.

Risks and test signals: debugging and observability tools can generate legitimate events; the b32 broad tracing rule is commented. Test with controlled ptrace operations and key searches.
