# sources/test-tools/ltp/testcases/kernel/fs/doio/include/forker.h

Purpose: `forker.h` declares process-backgrounding and process-copy helpers used by the doio filesystem stress programs. It also exposes the global pid table that callers can use for later coordination.

Important APIs and types: `FORKER_MAX_PIDS` is 4098. `Forker_pids` stores forked process ids and `Forker_npids` stores the number of pid entries known to the current process. Public functions are `background(char *)` and `forker(int, int, char *)`.

Control flow: no implementation is present, but comments define `background()` as parent-exits/child-continues detachment. `forker()` creates `ncopies - 1` additional processes; mode 0 creates first-generation children and mode 1 creates a descendant chain.

State and persistence behavior: pid arrays are copied by fork and then diverge per process. Consumers must account for incomplete pid knowledge in some process topologies. Process state persists outside the caller until normal process exit or explicit signaling by the test.

Dependencies and integration points: `forker.c` implements the API. `growfiles.c` uses it for `-b`/background default behavior, `-n` multiple workers, and optional synchronized stop notification.

Risks: exposed globals invite callers to depend on process-local snapshots. The fixed pid table can truncate for high fan-out. The API cannot express child reaping or cleanup responsibilities.

Test signals: callers should validate process counts, mode-specific parent/child return values, and whether enough pids are available for signal fan-out in the intended topology.
