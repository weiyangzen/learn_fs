# sources/test-tools/strace/src/retval.h

Purpose: Declares return-value formatting APIs and flag conventions shared between syscall decoders and the syscall dispatch layer.

Important APIs/types/functions: prototypes and flag definitions for return-value handling.

Control flow: header-only; decoders communicate desired result style by returning flags declared here.

State and persistence: none.

Dependencies/integration: included widely by core decoding code and syscall implementations through `defs.h`.

Risks: flag value changes would break decoder semantics globally.

Test signals: full strace test suite build and output comparison for all return-value styles.
