# sources/sync-backup/rsync/case_N.h

Purpose: macro include file that emits sequential `case N:` labels across repeated inclusions.

Important APIs/types/functions: preprocessor state macros `CASE_N_STATE_0`, `CASE_N_STATE_1`, etc. Each include defines the next state and emits a case label with fallthrough comments.

Control flow: used inside switch statements such as cleanup's reentry-safe state machine. Repeated inclusion advances the emitted case label without hand-maintaining numeric labels.

State and persistence: compile-time preprocessor state only; no runtime state.

Dependencies/integration: requires the includer to place it inside a `switch` and to avoid leaking state across unrelated uses unless reset by compilation unit boundaries.

Risks: unusual pattern is hard to read and can fail if included more times than supported labels or from an unexpected context.

Test signals: `cleanup.c` compile and cleanup-path CI indirectly validate generated labels.
