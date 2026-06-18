# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/driver.h

## Role

SBP-2 driver-interface and implementation-state header. It defines parsed Config ROM structures, target/LUN/session/task/agent state, statistics, lock annotations, and exported SBP-2 driver functions.

## Key Elements

- Config ROM structures:
  `sbp2_cfgrom_bib_t`, `sbp2_cfgrom_dir_t`, `sbp2_cfgrom_ent_t`, and `sbp2_cfgrom_t`.
- Task state and error enums track task lifecycle and completion failure source.
- `sbp2_task_t` tracks task list links, session, driver-private data, bus buffer, timeout, timeout ID, state/error, bus error, status block, and timing.
- `sbp2_agent_t` models a command block agent with mutex/CV, state, acquired flag, command buffers, active task, and agent register offsets.
- `sbp2_ses_t` represents a login session with login ID, command agent, status FIFO, task list, and status callback.
- `sbp2_lun_t` tracks one logical unit, its sessions, ORB freelist, login response, and reconnect/login state.
- `sbp2_tgt_t` tracks a target: bus handle, LUNs, parsed Config ROM, management agent state, management ORB/status buffers, login response buffer, and statistics.
- Defines lock-order and data-protection annotations for target, session, agent, task list, and LUN state.
- Declares target lifecycle, disconnect/reconnect/reset, Config ROM access, LUN lookup, LUN login/logout/reset, session reconnect/task submission/cancel/reset/abort, ORB alloc/free/sync, byte swapping, and Config ROM walking/query helpers.

## Dependencies and Coupling

Includes SBP-2 protocol definitions and bus interface headers. It is the central internal API consumed by SBP-2 target drivers.

## Research Notes

The state model separates target management-agent operations from per-LUN sessions and per-session task queues. Several fields are marked stable-data while mutable queue/task fields are protected by separate mutexes.
