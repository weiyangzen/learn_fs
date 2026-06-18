# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Stack.java

Purpose: thin wrapper around `java.util.Stack<StackEntry>` for the stack-machine test harness.

Important APIs and flow: exposes `push(int,Object)`, `push(StackEntry)`, `pop`, `swap`, `size`, and `clear`. `swap(index)` treats index as distance from top, validates bounds, and swaps the selected entry with the top entry.

State and persistence: in-memory stack only, shared through `Context.stack`. Dependencies are `StackEntry` and callers in `Instruction`, `Context`, and stack testers. Risks include synchronized legacy `java.util.Stack` semantics not guaranteeing higher-level thread safety, unchecked empty pops, and operation-index preservation depending on callers. Signal is indirect through stack-machine workloads.
