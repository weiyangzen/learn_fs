<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/caps0.h -->
## sources/test-tools/strace/src/caps0.h

Purpose: Lists low capability constants used to define the first capability mask enum.

Important APIs and types: Expands to enum entries from `CAP_CHOWN` through `CAP_SETFCAP`.

Control flow: Header fragment only; it is intended to be included inside an enum definition.

State and persistence: No state.

Dependencies and integration: Included by `capability.c` before `xlat/cap_mask0.h`. The order must match Linux capability numbers 0-31.

Risks: Missing or reordered entries would break symbolic capability decoding.

Test signals: Capability bitmask tests for low bits should print the expected `CAP_*` names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/caps0.h -->
