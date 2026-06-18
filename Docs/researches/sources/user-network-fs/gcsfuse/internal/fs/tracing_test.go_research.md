<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/tracing_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/tracing_test.go

Purpose: integration tests that every FUSE operation wrapper emits an OpenTelemetry server span with the expected gcsfuse tracing operation name, under both interrupt-handling modes.

Important APIs/types/functions: suite `TracingTestSuite`; helper `createTestFileSystemWithTraces`; `newInMemoryExporter`; tests `TestTraceLookupInode`, `TestTraceStatFS`, `TestTraceGetInodeAttributes`, `TestTraceSetInodeAttributes`, `TestTraceForgetInode`, `TestTraceMkDir`, `TestTraceMkNode`, `TestTraceCreateFile`, `TestTraceCreateLink`, `TestTraceCreateSymlink`, `TestTraceRename`, `TestTraceRmDir`, `TestTraceUnlink`, `TestTraceOpenDir`, `TestTraceReadDir`, `TestTraceReadDirPlus`, `TestTraceReleaseDirHandle`, `TestTraceOpenFile`, `TestTraceReadFile`, `TestTraceWriteFile`, `TestTraceSyncFile`, `TestTraceFlushFile`, `TestTraceReleaseFileHandle`, `TestTraceReadSymlink`, `TestTraceRemoveXattr`, `TestTraceGetXattr`, `TestTraceListXattr`, `TestTraceSetXattr`, `TestTraceFallocate`, and `TestTraceSyncFS`.

Control flow: each subtest builds a filesystem with tracing enabled and an in-memory OTEL exporter, creates fixture objects/inodes/handles when needed, invokes one FUSE method on the server, then asserts one exported span name and server span kind. Cases run for `IgnoreInterrupts` true and false.

State and persistence behavior: fake bucket and filesystem state are created per test. Span state is exported in memory and reset between tests. Some operations create or remove actual fake bucket objects to reach the target FUSE path.

Dependencies and integration points: exercises `NewFileSystem` plus `wrappers.WithTracing`, gcsfuse tracing constants, `otel/sdk/trace/tracetest`, fuseops structs, fake bucket, and server config.

Risks: because wrappers have one delegator per FUSE operation, missing or wrong operation names are easy regression points. Setup must create enough inode/handle state for each method without making the span assertion dependent on operation success.

Test signals: broad operation-name coverage across lookup, attrs, create, link, symlink, rename, directory operations, file read/write/sync/flush/release, xattrs, fallocate, and syncfs. It also validates span kind is server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/tracing_test.go -->
