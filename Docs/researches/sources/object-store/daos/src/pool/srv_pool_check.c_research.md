# sources/object-store/daos/src/pool/srv_pool_check.c

## Purpose
`srv_pool_check.c` implements the server-side pool "glance" path used by DAOS check and catastrophic recovery logic. It inspects stopped local pool storage, captures VOS target presence/state and pool-service RDB clues, and analyzes whether a set of pool-service replicas can still elect a leader or needs catastrophic recovery bootstrap from a best replica.

## Important APIs, types, and functions
The public entry points are `ds_pool_clue_init`, `ds_pool_clue_fini`, `ds_pool_clues_init`, `ds_pool_clues_fini`, `ds_pool_clues_print`, `ds_pool_clues_find_rank`, and `ds_pool_check_svc_clues`. The key data contracts come from `struct ds_pool_clue`, `struct ds_pool_svc_clue`, `struct ds_pool_clues`, and `struct rdb_clue`. Internally, `pool_glance` opens the pool service RDB and loads `ds_pool_prop_label`, `ds_pool_svc_load` metadata, RDB membership, and map version. `compare_logs` compares RDB last term/index pairs independently of the volatile current term.

## Control flow
`ds_pool_clue_init` initializes one clue for a pool UUID on one local directory class. For normal directories it first scans every VOS target file with `ds_mgmt_file(..., VOS_FILE, ...)` and `stat`, classifying targets as nonexistent, empty, or normal. It then checks for the pool-service RDB path and, if present, delegates to `pool_glance`. `pool_glance` opens storage with `rdb_open`, calls `rdb_glance`, starts a local transaction, reads the label, and loads the service map version and RDB clue. Errors are stored in `pc_rc` while UUID/rank/dir remain valid for reporting.

`ds_pool_clues_init` walks normal, newborn, and zombie pool directories through management iterators. `glance_at_one` applies an optional phase-producing filter, grows the clue array, and records a clue for each accepted UUID. `ds_pool_check_svc_clues` then evaluates a nonempty set of service clues for one pool: first it tries to find any voting replica with a majority of voting members whose logs are not newer than its own; if no such candidate exists, it chooses the replica with the newest pool map version and, among those, newest RDB log for catastrophic recovery advice.

## State and persistence behavior
This file reads persistent state without starting the pool service. Persistent signals include target VOS file existence and size, pool labels in RDB, pool-map version, RDB replica membership, voted rank, log term/index, snapshot base term/index, and object ID state. It intentionally only glances service RDBs from the normal pool directory, while target clues also record newborn and zombie directory membership. It owns heap allocations for labels, target status arrays, RDB replica lists, and clue arrays; `ds_pool_clue_fini` and `ds_pool_clues_fini` release these.

## Dependencies and integration points
The code integrates the DAOS management storage layout, RDB storage API, pool service loader, DAOS check fail injection, and system xstream assumptions. Callers must invoke it on xstream 0 with local pools stopped, because it opens RDB files directly and scans target files rather than using live pool handles. The catastrophic recovery advice is later consumed by pool check/recovery orchestration to decide whether normal service startup is possible.

## Risks and test signals
The main risks are misclassifying local corruption as absence, leaking partially allocated clues on RDB/read errors, and choosing a stale replica during catastrophic recovery. The label length check is a deliberate corruption guard. The disabled in-file tests document expected `compare_logs` and `ds_pool_check_svc_clues` cases: single-replica membership, missing voters, insufficient quorums, conflicting map versions, and newer log tie-breaks. External tests should exercise stopped-pool scanning, missing target files, corrupt labels, absent RDBs, and mixed RDB membership where only some replicas can get a majority.
