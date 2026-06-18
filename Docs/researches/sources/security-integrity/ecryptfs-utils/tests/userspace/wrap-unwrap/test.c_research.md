## sources/security-integrity/ecryptfs-utils/tests/userspace/wrap-unwrap/test.c

Purpose: C regression test for libecryptfs passphrase wrapping APIs. It verifies a known passphrase round trip, then exhaustively checks passphrase lengths from 1 through `ECRYPTFS_MAX_PASSWORD_LENGTH`, and finally verifies overlength input fails.

Important APIs and functions: `main`, `from_hex`, `ecryptfs_wrap_passphrase`, `ecryptfs_unwrap_passphrase`, `strlen`, `memcmp`. Control flow decodes the default salt, wraps to the supplied path with wrapping password `testwrappw`, unwraps and compares length/content, repeats for increasing passphrase lengths, then attempts an overlong passphrase and expects an error.

State and persistence: Writes and overwrites a wrapped-passphrase file at the path supplied by the shell wrapper; sensitive passphrase buffers are stack-resident and not wiped. Dependencies are libecryptfs and writable temporary storage. Integration is userspace library regression coverage. Risks include char generation beyond alphabetic range for long lengths, which is fine as byte data but can affect diagnostics.
