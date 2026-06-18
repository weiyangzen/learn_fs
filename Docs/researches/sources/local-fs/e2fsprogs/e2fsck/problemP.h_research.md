# File Research: sources/local-fs/e2fsprogs/e2fsck/problemP.h

This private header defines the internal structures and flags used by `problem.c`.

Core structures:
- `struct e2fsck_problem` stores one problem-table entry: code, localized description, prompt ID, behavior flags, optional chained problem code, runtime count, and max-count suppression threshold.
- `struct latch_descr` stores a latch group: latch code, question problem, end-message problem, and latch state flags.

Problem flags:
- `PR_PREEN_OK`: preen can answer automatically without halting.
- `PR_NO_OK`: a no answer does not mark the filesystem invalid.
- `PR_NO_DEFAULT`: default answer is no.
- `PR_MSG_ONLY`: print-only problem.
- `PR_FATAL`: fatal after reporting.
- `PR_AFTER_CODE`: ask/report another code after this one.
- `PR_PREEN_NOMSG`, `PR_NO_NOMSG`, `PR_PREEN_NOHDR`: suppress variants.
- `PR_NOCOLLATE`: avoid default answer collation.
- `PR_PREEN_NO`, `PR_FORCE_NO`: force no in certain modes.
- `PR_CONFIG`: profile overrides have already been applied.
- `PR_NOT_A_FIX`: yes answer is not counted as repaired corruption.
- `PR_HEADER`: structured pass header marker.

Integration points:
- Included by `problem.c` only.
- Complements the public problem-code declarations in `problem.h`.

Risk notes:
- Latch flag bit positions overlap intentionally with `PR_LATCH_MASK`; new flags must avoid the reserved latch bit range.
