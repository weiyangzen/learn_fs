# sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_cxx_swift_value_conformance.swift

Purpose: Forces Swift value witness/conformance exposure for selected FDBServer/FDBClient request types so C++ can use them in generated Swift interop contexts.

Important APIs/types/functions: `@_expose(Cxx) public struct ExposeTypeConf<T>` is a generic carrier. Four `@_expose(Cxx)` functions accept `ExposeTypeConf<UpdateRecoveryDataRequest>`, `ExposeTypeConf<GetCommitVersionRequest>`, `ExposeTypeConf<GetRawCommittedVersionRequest>`, and `ExposeTypeConf<ReportRawCommittedVersionRequest>`.

Control flow: Functions are no-op markers; the effect happens at compile/header generation time, not runtime.

State and persistence behavior: No state. The functions do not read or mutate values.

Dependencies and integration points: Imports `FDBClient`, `FDBServer`, and `flow_swift`. Integrated with Swift/C++ generated headers where these request types otherwise cannot be used in Swift generic contexts from C++.

Risks: Manual maintenance burden: every additional bridged type with the same generic-context error needs a matching expose function. The file uses underscored Swift attributes, so it is sensitive to Swift interop evolution.

Test signals: Build success is the primary signal. Failures appear as C++/Swift interop compile errors involving missing value witness exposure for request types.
