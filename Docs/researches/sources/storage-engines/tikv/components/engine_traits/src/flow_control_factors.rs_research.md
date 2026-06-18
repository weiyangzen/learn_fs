# sources/storage-engines/tikv/components/engine_traits/src/flow_control_factors.rs

Purpose: Declares an extension point for retrieving storage-engine flow-control factors.

Important APIs and control flow: `FlowControlFactorsExt` exposes `get_flow_control_factors_cf(&self, cf) -> Result<(u64, u64)>`, returning backend-defined factors for a CF.

State, persistence, and dependencies: State is read from backend engine metrics/options; the trait itself has no storage.

Integration points, risks, and test signals: Used by `MiscExt` supertrait bounds and write-stall/flow-control logic. Risks are unclear semantics of the returned tuple, unsupported CFs, and stale metrics. Signals come from backend flow-control tests and runtime throttling behavior.
