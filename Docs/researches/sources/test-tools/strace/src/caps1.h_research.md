<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/caps1.h -->
## sources/test-tools/strace/src/caps1.h

Purpose: Lists high capability constants used to define the second capability mask enum.

Important APIs and types: Expands to entries `CAP_MAC_OVERRIDE` through `CAP_CHECKPOINT_RESTORE`.

Control flow: Header fragment only; included inside an enum.

State and persistence: No state.

Dependencies and integration: Included by `capability.c` before `xlat/cap_mask1.h`. These entries represent `CAP_TO_INDEX` high-word capability values.

Risks: New kernel capabilities above this list will decode as unknown until this file and xlat data are updated.

Test signals: Capability bitmask tests for high bits should print `CAP_BPF`, `CAP_PERFMON`, and `CAP_CHECKPOINT_RESTORE` correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/caps1.h -->
