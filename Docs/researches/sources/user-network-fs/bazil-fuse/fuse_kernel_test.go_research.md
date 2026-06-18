# sources/user-network-fs/bazil-fuse/fuse_kernel_test.go

Purpose: This unit test file validates `OpenFlags` access-mode helpers and string formatting.

Important APIs, types, and functions: Tests cover `OpenAccessModeMask`, `OpenReadOnly`, `OpenWriteOnly`, `OpenReadWrite`, `IsReadOnly`, `IsWriteOnly`, `IsReadWrite`, and `OpenFlags.String`.

Control flow: Each test builds an `OpenFlags` value from `os.O_*` flags, checks the masked access mode, then verifies the boolean helpers. `TestOpenFlagsString` expects combined access and modifier flags to format as `OpenReadWrite+OpenAppend+OpenSync`.

State and persistence behavior: No persistent state. Tests are deterministic and in-process.

Dependencies and integration points: Uses Go `os` constants and the public `bazil.org/fuse` API from an external test package, which helps verify exported behavior.

Risks: Coverage is intentionally narrow. It does not test all open flags, unknown flags, platform-specific `openFlags`, or kernel message decoding.

Test signals: Provides a focused regression guard for access-mode masking, which is easy to get wrong because access modes are not independent one-bit flags.
