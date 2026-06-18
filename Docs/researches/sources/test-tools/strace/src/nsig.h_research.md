<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nsig.h -->
# sources/test-tools/strace/src/nsig.h

Purpose: normalizes `NSIG` availability and defines signal-set byte size.

Important APIs/types/functions: `NSIG` fallback/error checks and `NSIG_BYTES`.

Control flow: preprocessor-only logic warns and uses 32 if `NSIG` is missing, errors if it is less than 32, then defines `NSIG_BYTES`.

State and persistence behavior: no state.

Dependencies and integration points: includes `<signal.h>`; used by signal mask decoders and syscall wrappers that need kernel sigset sizing.

Risks: assumes `NSIG / 8` is an adequate byte count for kernel sigset operations in callers.

Test signals: build on platforms with and without `NSIG`, and ppoll/pselect sigset-size decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nsig.h -->
