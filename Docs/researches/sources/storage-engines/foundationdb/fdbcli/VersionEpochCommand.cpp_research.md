# sources/storage-engines/foundationdb/fdbcli/VersionEpochCommand.cpp

## Purpose

`VersionEpochCommand.cpp` implements `fdbcli versionepoch`, which reads, enables, disables, sets, and commits the cluster version epoch. Version epoch lets assigned versions track wall-clock-derived expected versions and supports a one-time jump through `advanceVersion`.

## Important APIs, Types, and Functions

- `versionEpochSpecialKey` is `\xff\xff/management/version_epoch`, the management special key used for CLI get/set/clear.
- `VersionInfo` holds current read version and expected version.
- `getVersionInfo` reads `versionEpochKey` directly from system data and computes expected version from `g_network->timer() * CLIENT_KNOBS->CORE_VERSIONSPERSECOND - versionEpoch`.
- `getVersionEpoch` reads the management special key and parses the value with `boost::lexical_cast<int64_t>`.
- `versionEpochCommandActor` implements the full command grammar.
- `advanceVersion(cx, expectedVersion)` performs the irreversible version jump for `commit`.

## Control Flow

With no arguments, the actor reports current version, expected version, and their difference, or says the epoch is unset. `get` reads the special key and prints its integer value. `disable` clears the special key if present. `enable` sets epoch `0` if unset; if already set, it prints the commit warning. `set <EPOCH>` parses a signed integer and sets the special key when absent or different. `commit` computes expected version and calls `advanceVersion`; if the epoch is unset it prints a prerequisite message. All mutating paths retry transactions through `onError`.

## State and Persistence Behavior

The command persists the version epoch through the management special keyspace using `SPECIAL_KEY_SPACE_ENABLE_WRITES`. The no-argument reporting path reads `versionEpochKey` directly with `READ_SYSTEM_KEYS`. Committing does not change the epoch key; it advances the database version to the current expected version through the management API.

## Dependencies and Integration Points

This command integrates with management special keys, direct system data, `advanceVersion`, Flow timers, client knobs, and CLI dispatch. The command help emphasizes irreversibility because large version jumps cannot be undone.

## Risks and Edge Cases

`disable` checks presence by creating a separate transaction for `getVersionEpoch`, then clears using another transaction; a concurrent change can race, although retries handle normal conflicts. `enable` uses `getVersionEpoch(tr)` with the same transaction, while `disable` does not. `boost::lexical_cast` parse failures in `getVersionEpoch` are handled by transaction retry even though malformed special-key output may not be retriable. Very large expected-version differences can lead to disruptive version jumps.

## Test Signals

`fdbcli_tests.py` actively tests unset reporting, `get`, `commit` before setup, `enable`, `set 10`, `disable`, re-enable, and `commit` output prefix. It then waits for full recovery because committing can trigger recovery. Additional coverage should check invalid epoch syntax and idempotent set behavior.
