# sources/storage-engines/badger/badger/cmd/bank.go

Purpose: implements the `badger bank` Jepsen-inspired stress workload and a `disect` diagnostic command for transaction invariant failures.

Important APIs and flow: bank state is `account:<id>` keys with initial balance 100. `moveMoney` updates two accounts transactionally; `seekTotal` validates the invariant that total balance equals `numAccounts * initialBal`; `runTest` initializes accounts with `WriteBatch`, starts concurrent transfer goroutines, a read-check goroutine, and optional stream/subscriber verification DBs. `runDisect` opens the DB read-only in managed mode, scans min/max versions, binary-searches for the first invalid timestamp with `findFirstInvalidTxn`, and prints account diffs via `compareTwo`.

State and persistence: test mutates a Badger DB under `--dir`, optionally encrypted; stream/subscriber checks create temp DBs. Dependencies are Cobra, Badger transactions, streaming, subscriptions, protobuf, atomics, and timers. Risks: global flags/state make tests order-sensitive, logging the encryption key is intentional but sensitive, random account selection uses global `rand`, and `disect` spelling is part of the CLI. Test signals include CI bank workflows, race-enabled runs, optional stream/subscriber modes, and dissection output after invariant failure.
