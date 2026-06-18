## sources/storage-engines/foundationdb/bindings/flow/tester/DirectoryTester.cpp

Purpose: instruction implementations for a Flow binding directory/subspace tester. It adapts stack-based test instructions into calls on `IDirectory`, `DirectoryLayer`, `DirectorySubspace`, and `Subspace`.

Important APIs and functions: helpers `popTuples`, `popTuple`, `popPaths`, `pathToString`, `combinePaths`, and `logOp` decode tester stack values. Registered instruction structs implement `DIRECTORY_CREATE_SUBSPACE`, `DIRECTORY_CREATE_LAYER`, `DIRECTORY_CHANGE`, `DIRECTORY_SET_ERROR_INDEX`, create/open/move/remove/list/exists operations, key pack/unpack/range/contains, subspace open, logging, and strip-prefix.

Control flow: each instruction pops encoded tuples/paths from `data->stack`, obtains the current directory/subspace from `data->directoryData`, performs async calls with `instruction->tr`, optionally through `executeMutation`, then pushes results or new directory/subspace handles. Logging is gated by `LOG_OPS`/`LOG_DIRS`.

State and persistence: mutating instructions write directory metadata/content through the transaction. Logging instructions write diagnostic tuples under caller-provided prefixes. Tester state stores a list of directory/subspace handles and current/error indices.

Dependencies and integration points: includes `Tester.h`, uses tuple and directory APIs from the Flow binding, and registers instruction handlers through `REGISTER_INSTRUCTION_FUNC`.

Risks: stack encoding must match the external tester protocol exactly. Some debug output in `DIRECTORY_CREATE_LAYER` prints `nodeSubspace` for both node and content subspace, which can confuse diagnostics. Error behavior depends on `executeMutation`.

Test signals: primary behavior test harness for Flow directory/subspace compatibility.
