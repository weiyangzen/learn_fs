# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/dstep.c

SPIN deterministic-step code generator.

Key behavior:
- Generates verifier C code for Promela `d_step` sequences.
- Collects and emits guard tests for deterministic selections.
- Rejects constructs illegal inside `d_step`, including nested `d_step`, nested atomic, process termination, `run`, and remote references.
- Tracks generated labels and goto targets inside d_step sequences.
- Emits save/restore-related verifier code and reached-state bookkeeping.

Important details:
- Maintains arrays of source labels and destination labels with a `MAXDSTEP` cap.
- Detects gotos that break out of a `d_step`.
- Special-cases break destinations and selection options.
- Uses global flags such as `GenCode`, `IsGuard`, `TestOnly`, and `NextLab`.

Filesystem relevance:
- None directly; vendored SPIN model-checker code generation logic.
