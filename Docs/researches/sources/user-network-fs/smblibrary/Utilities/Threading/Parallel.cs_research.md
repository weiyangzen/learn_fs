# sources/user-network-fs/smblibrary/Utilities/Threading/Parallel.cs

Purpose: `Parallel` provides a C# 2.0-era parallel for-loop implementation.

Important APIs/types/functions: delegates `ForDelegate` and `DelegateProcess`; overloads `For(fromInclusive,toExclusive,delegate)`, `For(...,chunkSize,delegate)`, and `For(...,chunkSize,threadCount,delegate)`.

Control flow: a shared `index` is advanced by `chunkSize` under a lock; each async delegate processes its chunk until it reaches `toExclusive`; the caller waits with `EndInvoke` for all delegates.

State and persistence behavior: no persistent state; parallel work can mutate caller-owned state.

Dependencies and integration points: uses `Environment.ProcessorCount`, delegates, and asynchronous delegate invocation.

Risks: exceptions propagate from `EndInvoke` but other workers may have already run. No cancellation. Invalid `chunkSize <= 0` can loop incorrectly. The name conflicts with `System.Threading.Tasks.Parallel` in newer code.

Test signals: coverage for chunk boundaries, out-of-order execution, exceptions, custom thread count, invalid chunk size, and inclusive/exclusive range correctness.
