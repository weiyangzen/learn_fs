# sources/sync-backup/kopia/internal/iocopy/iocopy_test.go

Purpose: tests shared-buffer allocation/reuse and copy behavior for normal and error paths.

Important APIs/types/functions: `iocopy.GetBuffer`, `ReleaseBuffer`, `Copy`, `JustCopy`, `errorWriter`, `customReader`, and `customWriter`.

Control flow: buffer tests check length and pointer reuse after release. Copy tests stream a fixed string into `bytes.Buffer`, assert byte count and content, and verify write errors propagate through both `Copy` and `JustCopy`. Custom reader/writer wrapper types avoid standard fast paths and exercise the buffer-copy path.

State/persistence behavior: tests mutate the package-global buffer pool by releasing and retaking a buffer. No durable state exists.

Dependencies/integration: uses `strings.Reader`, `bytes.Buffer`, `io`, and `testify/require`.

Risks/test signals: tests do not cover concurrent buffer use or invalid buffer release. Pointer-reuse assertion relies on immediate freelist reuse, which matches current implementation.
