# sources/test-tools/stress-ng/stress-randlist.c research

Purpose: implements `randlist`, a memory stressor that builds a randomly ordered linked list of variable-sized items and repeatedly writes/verifies each node's data payload.

Important APIs, types, and functions: `stress_randlist_item_t` contains `next`, `dataval`, an allocation-type bit, and flexible payload data. `stress_randlist_free_item()` releases heap or mmap-backed nodes. `stress_randlist_exercise()` walks the list twice: first filling incrementing byte values, then optionally verifying payload integrity.

Control flow: `stress_randlist()` resolves item count, payload size, and compact mode. It allocates a temporary pointer array and either one compact heap block or individual nodes, occasionally using anonymous mmap for large item sizes. It shuffles the pointer array, links nodes in shuffled order, frees the pointer array, synchronizes, and loops exercising the list and incrementing bogo ops until stopped or verification fails.

State and persistence: all state is heap or anonymous mmap memory freed after the run. The list order is randomized per worker and there is no persistent output.

Dependencies and integration: uses stress-ng random generators, mmap population, prefetch builtin, memory-free reporting, and option parsing. It registers as `CLASS_MEMORY` with optional verification.

Risks: maximize options can request enormous item counts and may exhaust memory. Partial allocation cleanup paths must use the correct count and allocation mode. Verification only detects payload corruption after a fill pass; it does not validate list topology beyond successful traversal.

Test signals: allocation skip messages, heap/mmap allocation debug counts, optional data-check failure logs, bogo ops per full traversal, and clean release of compact or per-node allocations.
