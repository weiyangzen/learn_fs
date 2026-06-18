# sources/storage-engines/foundationdb/flow/task_priority_support.swift

Purpose: This Swift interop helper maps FoundationDB `Flow.TaskPriority` values into Swift `_Concurrency.TaskPriority` values and back to Flow/net2 priorities. It exists because Swift task priorities are byte-sized raw values while Flow priorities are the authoritative scheduler constants used by the C++ runtime.

Important APIs and types: The key API is `Flow.TaskPriority.asSwift`, backed by private `Repr: UInt8`; the `_Concurrency.TaskPriority` extension exposes static properties for each Flow priority, `rawValueNet2`, `name`, and `flowDescription`. The switch bodies enumerate scheduler priorities from `Max`, `RunLoop`, and IO/socket priorities through proxy, TLog, blob worker, restore, low, and zero priorities.

Control flow: Conversion is table-driven through exhaustive switch statements. A Flow priority becomes the corresponding byte `Repr` value for Swift scheduling; a Swift priority is matched against the static properties to recover the Flow raw value or display name. Unknown Flow enum cases and unknown Swift raw values fail fast with `fatalError` or render as `<unknown:...>` for names.

State and persistence behavior: There is no persisted state. Runtime state is only the raw priority value carried by Swift tasks. The private `Repr` enum is an ABI-adjacent compatibility table: changing it must stay synchronized with the C++/Swift bridge functions referenced in comments.

Dependencies and integration points: It imports `Flow` and integrates Swift concurrency tasks with Flow's net2 scheduler priority ordering. Callers can use `.DefaultEndpoint`, `.DiskRead`, `.LowPriorityRead`, and related properties in Swift code while preserving Flow's scheduling semantics when jobs are enqueued into the C++ runtime.

Risks: The main risk is drift between `Repr`, `Flow.TaskPriority`, and bridge functions such as `swift_priority_to_flow`/`swift_priority_to_net2`. `DefaultEndpoint` intentionally overlaps with Swift predefined priorities, so accidental use of generic Swift priorities can produce fatal errors in `rawValueNet2`. Tests should verify round-trip mappings for every priority, exact raw Flow values, unknown-value behavior, and scheduler ordering expectations.
