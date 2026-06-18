# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.h

Declares dictionary parameter extraction helpers.

Key points:
- Forward-declares `gs_matrix` and `gs_uid`.
- Documents common return convention: 0 valid, 1 defaulted, negative error; null-aware routines return 2 for null.
- Notes dictionary keys are passed as C strings to avoid GC concerns over static name refs.
- Declares scalar, array, procedure, matrix, UID, and UID-checking functions.
- Documents array helper variants for custom under/over errors, max length, and exact length.

Research notes:
- This is a shared validation layer for font, color, device, and interpreter parameter dictionaries.
