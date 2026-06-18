# sources/storage-engines/tikv/components/raftstore/src/coprocessor/mod.rs

## Purpose
`mod.rs` is the public interface for raftstore coprocessors. It declares the hook traits, command observation data structures, region-change and role-change event types, and re-exports the concrete dispatcher, split-check, consistency-check, read/write, and region-info APIs.

## Important APIs, Types, And Functions
`Coprocessor` provides `start`/`stop`. `ObserverContext` wraps the current region and the `bypass` flag used by dispatcher loops. Hook traits include `AdminObserver`, `QueryObserver`, `ApplySnapshotObserver`, `SplitCheckObserver`, `PdTaskObserver`, `RoleObserver`, `RegionChangeObserver`, `RegionHeartbeatObserver`, `RaftMessageObserver`, `CmdObserver`, `ReadIndexObserver`, `UpdateSafeTsObserver`, `DestroyPeerObserver`, and `TransferLeaderObserver`.

`RegionState` and `ApplyCtxInfo` describe apply-time state visible to exec observers. `Cmd` carries raft index, term, request, and response. `ObserveId`, `ObserveHandle`, and `CmdObserveInfo` track whether CDC, resolved-ts, and PiTR observation streams are active. `ObserveLevel` summarizes observation scope as `None`, `LockRelated`, or `All`. `CmdBatch` groups applied commands with observe IDs and region id and can estimate memory size.

## Control Flow
The dispatcher invokes default no-op trait methods unless registered observers override them. `CmdObserveInfo::observe_level` chooses the maximum active observation level: CDC and PiTR require all data, resolved-ts requires lock-related data, and inactive handles contribute `None`. `CmdBatch::push`, `extend`, and `into_iter` assert that region and observe IDs match, preventing accidental cross-region or stale-observer mixing.

## State And Persistence Behavior
This module defines state passed between raftstore and observers but does not persist data itself. `ObserveHandle` state is shared via an `Arc<AtomicBool>`, allowing observers to stop observation without mutating batches already carrying IDs. `CmdBatch::size` estimates only successful non-admin put/delete command payloads.

## Dependencies And Integration Points
The module binds `engine_traits`, `kvproto`, `pd_client`, `raft`, raftstore snapshot/store types, split-check modules, read/write wrappers, and region-info accessor exports. It is the main API consumed by raftstore, CDC, backup-log/PiTR, resolved-ts, split, region-info, and consistency subsystems.

## Risks
Most default hooks are no-ops, so missing registration can fail silently. `CmdBatch` uses assertions for invariants, which is correct for internal misuse but can panic if callers combine wrong observe handles. `CmdBatch::size` is approximate and ignores some command types and error responses. Observer hook contracts are broad and run in sensitive raftstore paths, so implementors must avoid blocking and must honor region/epoch semantics.

## Test Signals
The local test covers `CmdObserveInfo::observe_level` combinations for CDC, resolved-ts, and PiTR active/inactive handles. Dispatcher tests cover most trait hook invocation paths.
