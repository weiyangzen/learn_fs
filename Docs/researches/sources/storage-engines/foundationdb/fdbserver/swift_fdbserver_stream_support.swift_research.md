# sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_stream_support.swift

Purpose: Adds Swift `FlowStreamOps` and callback protocol conformances for FDBServer request `FutureStream` types, enabling Swift async iteration over C++ Flow streams.

Important APIs/types/functions: Extensions cover `FutureStream_UpdateRecoveryDataRequest`, `FutureStream_GetRawCommittedVersionRequest`, `FutureStream_GetCommitVersionRequest`, and `FutureStream_ReportRawCommittedVersionRequest`. Each sets `Element`, `SingleCB`, and `AsyncIterator = FlowStreamOpsAsyncIteratorAsyncIterator<Self>`. Matching `FlowSingleCallbackForSwiftContinuation_*` types conform to `FlowSingleCallbackForSwiftContinuationProtocol` and define `AssociatedFutureStream`.

Control flow: No direct runtime flow; these conformances enable generic async-stream code paths in `flow_swift` to subscribe callbacks and produce async iterators.

State and persistence behavior: No stored state in this file. State lives in the underlying Flow streams and continuation callback objects.

Dependencies and integration points: Imports `Flow`, `flow_swift`, `FDBClient`, `FDBServer`, and `Cxx`. It is the FDBServer-specific stream bridge companion to generic Flow Swift support and is validated by Swift stream tests.

Risks: Every C++ stream type requires exact pairing between the future stream and callback type. A mismatched associated stream would compile incorrectly or fail at interop boundaries. The file name in the header comment contains a typo (`strem`), documentation-only.

Test signals: Build checks conformance completeness. Runtime signal comes from Swift tests that await/iterate Flow streams and from any FDBServer Swift actor code consuming these request streams.
