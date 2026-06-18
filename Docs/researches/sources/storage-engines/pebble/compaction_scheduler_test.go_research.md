# sources/storage-engines/pebble/compaction_scheduler_test.go

Purpose: Datadriven-tests `ConcurrencyLimitScheduler` with fake time and a fake `DBForCompaction`, validating grant accounting without real DB compactions.

Important APIs/types/functions: `testTimeSource` and `testTicker` provide a manually driven ticker. `testDBForCompaction` implements `GetAllowedWithoutPermission`, `GetWaitingCompaction`, and `Schedule`, recording trace output. `ongoingCompaction` stores an index and grant handle. `TestConcurrencyLimitScheduler` provides commands `init`, `set-allowed`, `set-waiting-count`, `try-schedule`, `tick`, `compaction-done`, and `unregister`.

Control flow: The test initializes the scheduler, mutates allowance/waiting counts, attempts direct schedules, manually ticks the periodic granter, and completes synthetic compactions by calling `Done` on stored handles. Each command prints callback traces and current synthetic state.

State and persistence: In-memory only. Fake DB state includes allowance, waiting count, next synthetic index, and active handles. Scheduler state is observed through callback order and active handles.

Dependencies and integration: Uses production scheduler interfaces, `datadriven`, `leaktest`, and `slices.Delete`. It isolates scheduler behavior from real DB internals while preserving the callback contract.

Risks: Textual expectations are order-sensitive. It does not test multi-DB/global scheduling, CPU measurement, or priority comparisons in `WaitingCompaction`.

Test signals: Good signal for default scheduler grant lifecycle: admission under allowance, denial at limit, grant-on-Done, grant-on-tick, grant-on-allowance-increase, and shutdown.
