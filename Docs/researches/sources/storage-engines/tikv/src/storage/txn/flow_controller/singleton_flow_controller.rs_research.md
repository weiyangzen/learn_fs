# sources/storage-engines/tikv/src/storage/txn/flow_controller/singleton_flow_controller.rs

## Purpose
`singleton_flow_controller.rs` implements engine-wide scheduler flow control for a single RocksDB engine. It throttles foreground writes before raftstore/apply work is blocked by RocksDB write stalls. It combines a byte-rate `Limiter` with probabilistic request dropping driven by compaction pending bytes.

## Important APIs, types, and functions
`EngineFlowController` owns a global `discard_ratio`, global `Limiter`, control channel, background checker handle, and `VersionTrack<FlowControlConfig>`. Public APIs are `new`, `empty`, `should_drop`, `consume`, `unconsume`, `enable`, `enabled`, `update_config`, and `is_unlimited`. The background worker is `FlowChecker<E>`, parameterized by `FlowControlFactorStore`. `CfFlowChecker` stores per-CF smoothers for memtables, L0 files, L0 production and consumption flow, pending compaction bytes, unsafe destroy range handling, and startup suppression flags.

## Control flow
`EngineFlowController::new` builds a millisecond-refill limiter, wraps config in `VersionTrack`, creates `FlowChecker`, and starts a named background thread. The thread listens for close/enable/disable messages and RocksDB `FlowInfo` events. Flush events update L0 production, memtable state, and L0 state. L0/L0Intra events update consumption and L0 state. Compaction events update pending compaction bytes. Timeout ticks update aggregate foreground write-flow statistics and metrics.

Memtable control initializes throttling from recent foreground write p90, then adjusts speed by roughly 1 MiB/s per memtable trend. L0 control slows speed by `K_INC_SLOWDOWN_RATIO` while above threshold and releases control when below threshold. Pending-compaction control maps log2 pending bytes from soft to hard limits into a discard ratio, smoothed by EMA. Unsafe destroy range can freeze pending-bytes control when compaction bytes jump artificially.

## State and persistence behavior
All state is in memory: smoother windows, limiter speed/statistics, atomic discard ratio, selected throttle CF, last speed, startup flags, metrics, and background thread lifecycle. It does not persist data to RocksDB; it only observes RocksDB factors and controls scheduler admission or delay. `Drop` sends `Msg::Close` and joins the checker thread.

## Dependencies and integration points
It depends on RocksDB `FlowInfo`, engine traits for CF names and flow factors, `tikv_util::Limiter` and `Smoother`, online config, scheduler metrics, and thread naming utilities. It integrates at the scheduler boundary: callers check `should_drop`, call `consume`, and sleep or reject based on the result.

## Risks
Control stability is the key risk. Too aggressive speed reduction can collapse QPS; too weak control allows RocksDB write stalls. Startup suppression must avoid throttling on inherited backlog while still detecting new accumulation. Pending compaction bytes are noisy, so log scaling and EMA must avoid both NaN from zero and stale high averages after destroy range. Background thread channel sends use `unwrap` in enable/disable, so lifecycle misuse can panic if called after channel closure.

## Test signals
Tests use an `EngineStub` to exercise facade behavior, memtable thresholds, L0 thresholds, pending compaction bytes, zero pending bytes, and unsafe-destroy-range jump control. Helpers are shared with tablet tests, giving parity signals between both flow-control modes.
