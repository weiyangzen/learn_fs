# sources/storage-engines/tikv/components/engine_traits_tests/src/scenario_writes.rs

Purpose: Parameterizes basic write/delete/range-delete behavior across direct engine APIs, CF APIs, and write-batch APIs.

Important APIs and control flow: `WriteScenario` selects non-CF, default-CF, other-CF, and write-batch variants. `WriteScenarioEngine` routes put/delete/delete-range/get calls to the selected API and verifies non-CF/default-CF reads agree. The `scenario_test!` macro expands each scenario into six modules. Cases cover missing values, put/get, deleting absent and present keys, inclusive/exclusive range deletes, all-in-range deletes, equal begin/end no-op, and reversed range panic/recovery.

State, persistence, and dependencies: Each scenario creates a temporary all-CF engine and mutates either default or write CF; write-batch scenarios persist through `WriteBatch::write`.

Integration points, risks, and test signals: Strong signal that direct and batched mutation APIs share semantics. Risks include CF routing errors, write-batch commit omissions, range bound handling, and reversed ranges not failing.
