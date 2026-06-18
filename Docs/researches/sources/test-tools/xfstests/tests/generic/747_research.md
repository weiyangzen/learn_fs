# sources/test-tools/xfstests/tests/generic/747


Purpose: Stresses zoned/GC behavior by filling an 8GiB scratch filesystem to 95 percent with random-size direct writes, then mixing direct and buffered writes with random deletes to force reclaim and fragmentation.


Important APIs, helpers, and commands: Shell helpers `_create_file`, `_total_M`, `_used_percent`, `_delete_random_file`, `_get_random_fsz`, `_direct_fillup`, `_mixed_write_delete`; xfstests gates `_require_scratch` and `_require_no_compress`.
 Local helper functions detected in the file include `_create_file`, `_delete_random_file`, `_direct_fillup`, `_get_random_fsz`, `_mixed_write_delete`, `_total_M`, `_used_percent`.
 It imports `./common/preamble`.
 Capability gates include `_require_no_compress`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: Seeds `$RANDOM`, formats and mounts scratch, fills with direct I/O until the target usage, runs a direct mixed write/delete pass, runs a buffered pass, then syncs. The state is scratch files `data_$testseq`, filesystem free-space counters, and the PRNG seed in `$seqres.full`; all persistent effects are disposable scratch contents. Dependencies are `dd`, `stat -f`, `find`, `shuf`, scratch mkfs/mount/sync helpers, and a non-compressed filesystem. Main risks are space accounting drift, random delete finding no file, direct-I/O alignment, and runtime on slow zoned devices. Success is absence of write failures plus the printed phase markers and final sync. Source size is 119 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
