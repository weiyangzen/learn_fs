# sources/storage-engines/tikv/components/health_controller/src/slow_score.rs

Purpose: AIMD slow-score algorithm for disk and network inspection timeouts, bounded conceptually between healthy `1` and very slow `100`.

Important APIs/types/functions: constants for disk/network thresholds and recovery; `SlowScore::{new,new_with_extra_config,record,record_timeout,tick,update,get}`; `SlowScoreTickResult`.

Control flow: records are accepted only for the current tick ID. Finished ticks count total requests and timeout requests. `tick` advances the ID, marks a new unfinished tick, and updates only at round boundaries. Update decreases linearly with no timeouts and increases multiplicatively according to timeout ratio capped by the configured threshold.

State and persistence: in-memory counters, `Instant`s, tick ID, unfinished flag, and `OrderedFloat` score/ratio.

Dependencies/integration: used by `UnifiedSlowScore` in reporters; depends on `ordered_float`.

Risks: records with mismatched IDs are silently ignored; update math assumes timeout requests imply total requests; scheduling delays affect recovery elapsed time.

Test signals: unit tests verify score growth, recovery, KvDB extra config, and minimum round-tick behavior.
