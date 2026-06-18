<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/userent.h -->
# sources/test-tools/strace/src/linux/x86_64/userent.h

Purpose: maps x86_64 and inherited i386 user-register offsets to printable names.
Important APIs/types/functions: includes `../i386/userent0.h` then adds x86_64-specific names such as `r15`, `orig_rax`, `rip`, segment bases, and segment registers.
Control flow: declarative table only. State and persistence behavior: static lookup data.
Dependencies and integration points: register printing, poking, and diagnostics. Risks: wrong offsets make register names misleading and can affect user-facing tampering diagnostics. Test signals: register-name lookup tests for x86_64 and compat registers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/userent.h -->
