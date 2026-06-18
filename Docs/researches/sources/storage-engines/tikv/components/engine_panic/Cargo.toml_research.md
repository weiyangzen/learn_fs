# sources/storage-engines/tikv/components/engine_panic/Cargo.toml

Purpose: Declares the `engine_panic` crate, an example/skeleton TiKV engine implementation whose methods panic. It exists to satisfy and document the broad `engine_traits` surface for alternative engines.

Important APIs and types: Package metadata sets edition 2021, unpublished Apache-2.0 crate, and feature `testexport`. Dependencies include `engine_traits`, `encryption`, `kvproto`, `raft`, `tikv_util`, `tracker`, and `txn_types`.

Control flow and state: Cargo metadata only; no runtime behavior. The dependency list mirrors trait areas implemented by the panic modules, including raft log APIs, SST encryption hooks, perf tracking, and transaction timestamp types.

Integration points: Builds as a workspace component and provides a compile-time template for engine implementors.

Risks: Because implementations panic, accidental production use would fail immediately. The manifest keeps dependencies broad enough that trait drift is caught at compile time.

Test signals: No tests in the manifest; compile success is the main signal that the skeleton still satisfies required traits.
