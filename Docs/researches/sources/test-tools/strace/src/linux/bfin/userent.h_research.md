# sources/test-tools/strace/src/linux/bfin/userent.h

Purpose: defines `bfin` `ptrace(PEEKUSER)`/`struct user` offset names for strace's user-area decoders, with 8 visible entries.

Important APIs/types/functions: xlat initializer rows or `XLAT_UOFF` macros map offsets to register/user-field names; no executable functions are defined.

Control flow: ptrace/user-offset printing indexes these rows when a trace asks for user-register offsets.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes userent0.h.

Risks/test signals: wrong offsets make `PTRACE_PEEKUSER` output misleading; validate against the architecture `struct user` layout and register-offset trace tests.

Source-read signal: reviewed complete local file (16 lines).
