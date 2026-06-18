<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/heal.rs -->
# sources/object-store/rustfs/crates/config/src/constants/heal.rs

## Purpose
Defines the heal admin subsystem name, supported config keys, and environment/default values for automatic healing, heal queue behavior, concurrency, per-set bulkheads, page parallelism, and scanner-driven bitrot cycles.

## Important APIs, types, and functions
Exports `HEAL_SUB_SYS`, `HEAL_BITROT_CYCLE`, `HEAL_KEYS`, and `DEFAULT_HEAL_BITROT_CYCLE_SECS`. Runtime knobs include auto-heal enable, queue size, interval, task timeout, global/per-set concurrency, low-priority merge/drop behavior, page object concurrency, event-driven wakeups, set bulkheads, and page parallel enablement.

## Control flow
No code executes in this file. Heal managers and admin config parsers use the constants to configure queues, schedulers, and repair workers.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with heal queue admission, erasure-set repair schedulers, scanner bitrot/deep-scan configuration, and admin config storage.

## Risks and edge cases
Defaults enable auto-heal and event-driven scheduling, so misconfigured environments can increase repair load. Queue size and concurrency constants directly affect memory and disk pressure. Per-set concurrency must remain aligned with scheduler fairness assumptions.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Heal runtime tests should cover queue-full low-priority behavior, duplicate merge, per-set concurrency limits, and event-driven wakeups.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/heal.rs -->
