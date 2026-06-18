## sources/user-network-fs/go-fuse/fuse/attr.go

Purpose: utility methods for converting and inspecting FUSE attribute structs.

Important APIs/types/functions: `Attr.IsFifo`, `IsChar`, `IsDir`, `IsBlock`, `IsRegular`, `IsSymlink`, and `IsSocket` inspect mode type bits. `SetTimes`, `ChangeTime`, `AccessTime`, and `ModTime` convert between Go `time.Time` and FUSE timestamp fields. `ToStatT` and `ToAttr` adapt `os.FileInfo` to syscall and FUSE attrs.

Control flow: conversions are direct field mapping helpers used by loopback and tests.

State and persistence: stateless helpers mutating only the provided `Attr`.

Dependencies and integration: used by loopback filesystems, node adapters, and stat tests for consistent kernel metadata.

Risks and test signals: mode bit or time conversion mistakes propagate into cache validation, permissions, and stat comparisons.
