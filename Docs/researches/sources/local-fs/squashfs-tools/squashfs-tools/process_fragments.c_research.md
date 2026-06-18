# File Research: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.c

Implements fragment-processing worker `frag_thrd()`, used after readers but before main file assembly. It computes a 16-bit BSD checksum for fragment candidates and detects all-zero sparse fragments.

For append and duplicate checking, `get_fragment()` retrieves fragment blocks from the fragment cache, reserve cache, pending fragment-writer cache, or existing output filesystem. It coordinates with `dup_mutex` and cache locking so multiple threads do not consume a fragment buffer before it is filled.

`get_fragment_cksum()` computes and caches checksums for all appended files sharing a fragment block. `frag_thrd()` uses checksum prefiltering plus `memcmp()` to identify duplicate single-fragment files and forwards either duplicate metadata or the original buffer to `to_main`.

The thread blocks termination signals and opens the destination filesystem only when duplicate checking requires reading old fragments.
