# sources/test-tools/stress-ng/stress-list.c

Purpose: implements `list`, a CPU/cache/memory search stressor for BSD `sys/queue.h` list families plus an internal singly-linked tail list.

Important APIs/types/functions: `list_entry_t` carries a value and a union of queue entry link fields. Compile gates define support for `CIRCLEQ`, `LIST`, `SLIST`, `STAILQ`, and `TAILQ`. Method functions insert all entries, search for every entry, remove all entries, and update per-method `stress_metrics_t`. `stress_list_all()` rotates across available methods.

Control flow: `stress_list()` resolves method and size, allocates entries, optionally installs a SIGALRM longjmp handler, initializes entry values, sync-starts, and loops invoking the selected method. After each pass it mutates every entry value with a random xor/rotate to perturb memory contents, increments bogo ops, and continues. On exit or signal jump it restores SIGALRM, emits searches-per-second metrics for methods with data, frees entries, and returns status.

State and persistence behavior: all list nodes are heap memory reused across iterations. Queue links are reset by each method. No filesystem state exists. Static rotation index in `stress_list_all()` persists per process.

Dependencies and integration points: depends on `sys/queue.h` macro availability and optional `sigsetjmp` support. Uses stress-ng settings, signal helpers, metrics, random, and process state. Registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`.

Risks: O(n^2) search behavior means max list size is intentionally expensive. `siglongjmp` from SIGALRM is used to escape long searches, so cleanup must tolerate partially modified lists. Queue macro availability differs across libc implementations.

Test signals: run each method and `all`, min/max sizes, and forced timeout. Expected signals are nonzero method metrics, no missing-entry failures, and clean SIGALRM restoration.
