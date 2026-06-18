## sources/test-tools/stress-ng/stress-unshare.c

Purpose: Implements `unshare`, exercising Linux namespace/resource unsharing across many forked children and flag combinations.

Important APIs/types/functions: `stress_unshare_info`, `check_unshare`, `enough_memory`, and `stress_unshare`; uses `shim_unshare`, clone flag permutations, mmap-shared metrics, OOM adjustment, and kill/reap helpers.

Control flow: builds a permutation list from available `CLONE_*` flags, then repeatedly forks up to 32 short-lived children. Each child optionally unshares a random flag combination and then tries individual flags such as `CLONE_FS`, `CLONE_FILES`, namespace flags, `CLONE_SYSVSEM`, `CLONE_THREAD`, `CLONE_SIGHAND`, and `CLONE_VM`, treating EPERM/EACCES/EINVAL/ENOSPC as expected.

State and persistence: per-child duration/count fields are stored in shared anonymous memory and summarized after the run; no persistent files.

Dependencies/integration: uses Linux `unshare`, memory pressure checks, OOM helpers, and stress-ng flag permutation utilities.

Risks: namespace creation can be expensive or permission-restricted; memory throttling prevents deep swap pressure. The root/newnet special case avoids excessive network namespace cost.

Test signals: `VERIFY_ALWAYS`; reports nanoseconds per unshare call and fails only on unexpected errno paths.
