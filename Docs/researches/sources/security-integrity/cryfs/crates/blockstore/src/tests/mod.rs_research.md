# sources/security-integrity/cryfs/crates/blockstore/src/tests/mod.rs

Purpose: This test module root wires together `high_level`, `low_level`, and `utils`, and exports macros that test blockstore implementations through both native and adapter-wrapped API surfaces. It is the bridge that lets one implementation be validated as low-level, high-level, and round-tripped through adapter layers.

Important APIs and flow: `instantiate_blockstore_tests_for_lowlevel_blockstore!` runs the low-level suite directly, wraps the low-level fixture into high-level fixtures with and without flushing, then double-wraps high-level back to low-level. `instantiate_blockstore_tests_for_highlevel_blockstore!` performs the symmetric high-level-first matrix and then wraps through low-level adapters.

State and persistence: The macros intentionally vary flushing behavior. That makes persistence and buffering semantics testable across adapter boundaries, especially where high-level stores may cache writes or low-level stores may require explicit flush-like transitions.

Dependencies and integration: This file depends on macro exports from the low-level and high-level test modules plus fixture adapters under `tests::low_level` and `tests::high_level`. It integrates implementation crates by letting each implementation invoke one macro and receive a full nested module test tree.

Risks and test signals: The wrapping matrix is valuable for detecting semantic mismatches between APIs, but macro expansion hides the generated test topology and can produce large compile-time output. Failures will surface in nested modules such as `wrapped_in_high_level::with_flushing`, which is useful but requires understanding the adapter path.
