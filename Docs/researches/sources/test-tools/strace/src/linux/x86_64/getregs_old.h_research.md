<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.h -->
# sources/test-tools/strace/src/linux/x86_64/getregs_old.h

Purpose: declares availability of the old x86 GETREGS fallback path.
Important APIs/types/functions: include guard plus `HAVE_GETREGS_OLD`.
Control flow: no runtime logic. State and persistence behavior: compile-time feature flag only.
Dependencies and integration points: generic register-fetch code conditionally includes `getregs_old.c`. Risks: stale feature wiring could compile fallback unintentionally. Test signals: configure/build tests that disable GETREGSET and still trace x86 syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.h -->
