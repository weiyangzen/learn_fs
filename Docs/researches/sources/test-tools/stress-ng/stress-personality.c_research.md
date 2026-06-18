# sources/test-tools/stress-ng/stress-personality.c

Purpose: `stress-personality.c` implements the `personality` stressor, cycling through Linux execution-domain/personality constants and restoring/querying personality state.

Important APIs/types/functions: the implementation is gated on `HAVE_PERSONALITY` and includes generated `personality.h` entries into a static `personalities[]` array terminated by `INVALID_PERSONALITY`. `stress_personality_supported()` skips if the generated list is empty. `stress_personality()` tracks per-personality failures in a boolean array.

Control flow: the stressor allocates a failure table, reports how many personalities will be attempted, synchronizes, and loops over all generated personalities until stop. For each personality it skips permanently failed entries, calls `personality(p)`, retrieves the current personality via `personality(0xffffffffUL)`, exercises an invalid random high personality, restores `p`, and counts a bogo op per full pass. If every real personality fails, it reports failure.

State and persistence behavior: state is process personality flags plus the heap `failed[]` table. There is no filesystem state and no child process. Failed personalities are remembered for the duration of the run to reduce repeated unsupported calls.

Dependencies and integration points: it depends on `sys/personality.h`, generated build-time personality constants, stress-ng sync/state helpers, random number helpers, memory-free reporting, and registers as `CLASS_OS` with `VERIFY_ALWAYS`.

Risks: personality availability is architecture and kernel dependent; many constants can fail legitimately. Personality changes may alter process behavior such as address layout or uname quirks, so restoring/querying within the same loop matters. Treating all entries failing as hard failure distinguishes unsupported constants from a completely nonfunctional interface.

Test signals: direct `--personality` should either skip due to no generated personalities or make bogo progress. Failure signals include inability to query with `0xffffffffUL`, all personalities rejected, or unsupported builds without the syscall/header.
