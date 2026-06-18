# sources/storage-engines/wiredtiger/test/suite/test_layered_follower16.py

## Purpose

This test verifies lazy stable-cursor opening on a layered follower. Before the follower has picked up a checkpoint, operations must not open the stable tree. After checkpoint pickup, reads and non-overwrite writes should open stable, while default-overwrite insert/update operations should not.

## Important APIs, Types, and Functions

Top-level operation helpers implement `insert`, `update`, `search`, `search_near`, `next`, `prev`, `remove`, `reserve`, `modify`, and `largest_key`. Scenario dimensions combine operation type, cursor overwrite mode, and transaction end mode (`rollback`, `commit`, `survive`). `get_stat` reads connection statistics, especially `layered_curs_open_stable` and `layered_curs_reopen_stable`.

## Control Flow

The leader creates and populates a layered string-key table. A follower opens the same table and replays the initial writes into ingest. The test opens a follower cursor, performs the scenario operation before checkpoint pickup, and asserts stable-open count remains zero. It then timestamps and checkpoints the leader, advances the follower checkpoint, repeats the same operation, ends or preserves the transaction according to the scenario, and checks whether stable opened.

## State, Persistence, and Dependencies

The file depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`. It uses timestamped transactions, follower ingest replay, disaggregated checkpoint transfer, cursor overwrite configuration, and connection statistics as persistent behavioral signals. `_insert_counter` avoids duplicate keys for non-overwrite insert scenarios.

## Risks and Test Signals

The test guards against premature stable cursor opening, missed stable opening after checkpoint pickup, and unnecessary stable reopen churn. A subtle risk is that operation semantics vary with overwrite and transaction state; the `opens_stable` predicate encodes the intended exception for overwrite insert/update. Strong signals are exact statistic assertions before and after checkpoint advancement across many cursor APIs.
