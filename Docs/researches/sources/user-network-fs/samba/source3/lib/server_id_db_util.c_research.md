# sources/user-network-fs/samba/source3/lib/server_id_db_util.c

## Purpose
This file adds a higher-level exclusive-name helper around `server_id_db`. It lets a process register a named role while pruning stale records for dead processes.

## Important APIs, Types, And Functions
`server_id_db_set_exclusive(struct server_id_db *db, const char *name)` adds the current process to the name, looks up all registered servers for that name, verifies exclusivity with `server_id_db_check_exclusive()`, and removes its own registration on failure. The checker compares each record with the current process, calls `serverid_exists()` for peers, returns `EEXIST` if another live process owns the name, and prunes dead peers with `server_id_db_prune_name()`.

## Control Flow
The function performs add, lookup, check/prune, cleanup-on-error. The source comment explicitly accepts a race where two simultaneous registrants can both see each other live and both fail with `EEXIST`.

## State And Persistence
State lives in the passed `server_id_db`. The helper mutates it by adding the caller, pruning stale peers, and removing the caller if exclusivity is not achieved.

## Dependencies And Integration Points
It depends on `lib/util/server_id_db.h`, current process identity from `server_id_db_pid()`, process liveness from `serverid_exists()`, and talloc temporary ownership. Daemon startup paths can use it to prevent duplicate singleton services.

## Risks And Test Signals
Known risk is the accepted concurrent registration race. Other risks are stale records when pruning fails and liveness false positives. Tests should simulate only-self registration, live peer `EEXIST`, dead peer pruning, lookup failure cleanup, and concurrent starts if singleton behavior matters.
