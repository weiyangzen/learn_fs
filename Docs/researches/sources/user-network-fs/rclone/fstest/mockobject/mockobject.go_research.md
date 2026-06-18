
# sources/user-network-fs/rclone/fstest/mockobject/mockobject.go

Purpose: package `mockobject` supplies lightweight `fs.Object` implementations for tests: a bare path-only object and a content-backed object with optional seek behavior.

Important APIs/types/functions: `Object` is a string-backed `fs.Object`; `New` constructs it. Most mutation/read methods on bare `Object` return `errNotImpl`. `SeekMode` selects no seek, `io.Seeker`, or rclone `RangeSeek` support. `ContentMockObject` adds `content`, `seekMode`, optional owning `fs.Fs`, unknown-size mode, and modtime. Public methods include `WithContent`, `SetFs`, `SetUnknownSize`, `Open`, `Size`, `Hash`, `ModTime`, and `SetModTime`.

Control flow: `Open` decodes `fs.SeekOption` and `fs.RangeOption`, rejects unsupported mandatory options, slices or seeks into a `bytes.Reader`, and wraps it in the requested closer type. `Hash` builds a one-hash multihasher and returns the digest for the requested hash.

State/persistence: all object data is in memory. `SetModTime`, `SetFs`, and `SetUnknownSize` mutate the mock object instance.

Dependencies/integration: integrated with rclone `fs.OpenOption`, `RangeOption`, `SeekOption`, `RangeSeek`, and `hash`. It is often used with `mockfs.AddObject`.

Risks: no bounds checks are added beyond Go slicing behavior, so invalid seek/range combinations can panic if callers pass impossible offsets. Bare `Object` has zero size and no content, so tests must choose `WithContent` when reads matter.

Test signals: no direct tests here, but it is a focused utility for testing object consumers against seek/range/unknown-size permutations.
