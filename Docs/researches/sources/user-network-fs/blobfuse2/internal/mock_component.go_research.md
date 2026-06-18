<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/mock_component.go -->
# sources/user-network-fs/blobfuse2/internal/mock_component.go

## Purpose
Generated GoMock implementation of the `internal.Component` interface for unit tests. It lets tests assert and stub calls across the Blobfuse2 component pipeline and file-system operation surface.

## Important APIs, Types, and Functions
`MockComponent` holds a `gomock.Controller` and `MockComponentMockRecorder`. `NewMockComponent` constructs the mock, and `EXPECT` exposes recorder methods. The mock implements component lifecycle (`Configure`, `GenConfig`, `Start`, `Stop`, `Name`, `SetName`, `Priority`, `NextComponent`, `SetNextComponent`) and filesystem operations including directory, file, symlink, chmod/chown, stats, block-list, stage, and commit methods. Return types mirror production contracts such as `*handlemap.Handle`, `*ObjAttr`, `*common.BlockOffsetList`, `*CommittedBlockList`, `*syscall.Statfs_t`, and error values.

## Control Flow and State
Most methods are thin wrappers around `m.ctrl.Call` with type assertions for returned values. Recorder methods call `RecordCallWithMethodType` so test code can set expectations. `RenameFile` mutates `arg0.DstAttr` timestamps after invoking the mock call when a destination attribute is present. `GenConfig` is a manual stub returning an empty string rather than a mocked expectation.

## Dependencies and Integration Points
Depends on `github.com/golang/mock/gomock`, `context`, `syscall`, `time`, Blobfuse2 `common`, `handlemap`, and internal option/attribute types. It is coupled to the exact `Component` interface; interface changes require regenerating or editing this file.

## Risks and Edge Cases
Because this is generated code with manual additions, drift risk is high when `Component` changes. Several recorder methods for `GetCommittedBlockList`, `StageData`, and `CommitData` pass `reflect.TypeOf((*MockComponent)(nil).TruncateFile)` instead of their own methods, which can make gomock diagnostics or method type checks misleading. `StreamDir` discards the mocked string continuation/token and always returns `""`; tests relying on paged directory streaming can get false confidence. `GenConfig` cannot be expected through gomock.

## Test Signals
The file itself is test support. Good downstream tests using it can validate component chaining, option propagation, and error paths without real storage. Weak signals arise if tests overfit to mock behavior that differs from production, especially timestamp mutation and stream-token handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/mock_component.go -->
