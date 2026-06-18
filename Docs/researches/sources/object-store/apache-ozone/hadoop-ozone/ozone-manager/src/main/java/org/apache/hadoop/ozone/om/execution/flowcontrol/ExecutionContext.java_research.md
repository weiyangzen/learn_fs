# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/ExecutionContext.java

Purpose: `ExecutionContext` is an immutable holder for the log index and Ratis `TermIndex` associated with request execution.

Important APIs and types: `of(long index, TermIndex termIndex)` constructs an instance. `getIndex` and `getTermIndex` expose fields. If termIndex is null, construction synthesizes `TermIndex.valueOf(-1, index)`.

Control flow: The only branch normalizes null term indexes to a sentinel term of -1.

State and persistence behavior: It is in-memory only and carries persisted-log coordinates from Ratis or test paths.

Dependencies and integration points: Request application and audit code can use it to pass transaction index and term information without carrying raw Ratis types everywhere.

Risks and test signals: The sentinel term may be misinterpreted if callers require a real term. Tests should cover null and non-null termIndex construction and index preservation.
