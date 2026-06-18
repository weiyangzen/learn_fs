# sources/test-tools/xfstests/tests/generic/750


Purpose: Runs fsstress while repeatedly triggering kernel memory compaction to expose folio migration and compaction deadlocks or crashes during filesystem write load.


Important APIs, helpers, and commands: Uses `_require_vm_compaction`, `_run_fsstress`, `_kill_fsstress`, `/proc/sys/vm/compact_memory`, and soak controls `LOAD_FACTOR`, `TIME_FACTOR`, `SOAK_DURATION`.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_vm_compaction`.
 Regression annotations include `_fixed_by_git_commit kernel d99e3140a4d3 \, _fixed_by_git_commit kernel 2e6506e1c4ee \`.



Control flow, state, dependencies, risks, and test signals: The script formats/mounts scratch, starts a background loop writing `1` to the compaction knob every five seconds while a runfile exists, then runs fsstress with write workload sized by CPU and time factors. State is the scratch tree, background compaction PID, runfile, and kernel VM compaction activity; no durable repo state is kept. Dependencies include writable proc compaction knob and fsstress. Risks include cleanup leaving compaction running, requiring root/proc permissions, and long runtime. Success is fsstress completion without kernel failure. Source size is 61 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
