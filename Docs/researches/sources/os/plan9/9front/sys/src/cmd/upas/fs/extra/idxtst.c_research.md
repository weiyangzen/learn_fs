# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/idxtst.c

This helper tests exclusive index-file opening behavior.

Key behavior:
- `exopen` retries opening/truncating or creating `testingex` with exclusive/temp lock-style mode.
- Distinguishes expected lock/not-found/already-exists errors from fatal errors.
- After opening exclusively, attempts `Bopen` for reading and reports whether both opened.

Integration and risks:
- Diagnostic for Plan 9 lock semantics used by `idx.c`.
