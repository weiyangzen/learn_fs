<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/userent.h -->
# sources/test-tools/strace/src/linux/x32/userent.h

Purpose: x32 user-register-name table shim.
Important APIs/types/functions: includes `../x86_64/userent.h`, sharing x86_64 register constants and names.
Control flow: no executable logic. State and persistence behavior: build-time alias only.
Dependencies and integration points: used by register printing and `-e inject`/ptrace diagnostics that reference architecture registers. Risks: x32-specific register naming differences would be hidden by the alias. Test signals: register dump and syscall tampering tests under x32 should show expected x86 register names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/userent.h -->
