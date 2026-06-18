# sources/test-tools/unionmount-testsuite/tests/sym1-trunc.py

Purpose: verifies `O_TRUNC` opens through a direct symlink to an existing file.

Important APIs and functions: five subtests combine `tr=1` with read-only, write-only, append write-only, read/write, and append read/write calls to `ctx.open_file()`.

Control flow: read-only truncate empties the target and reads empty content. Write and read/write cases truncate first, then write `q` or `p`; append with truncate also yields only the newly written byte.

State and persistence: target content is deliberately destroyed through the symlink. Follow-up reads prove truncation applied to the target file, not to the symlink object.

Dependencies and integration: relies on Linux open semantics and harness flag mapping for `O_TRUNC`. Exercises copy-up of truncated lower file data under overlay.

Risks: `O_TRUNC|O_RDONLY` behavior can be platform-sensitive; this suite encodes the expected Linux behavior used by the harness.

Test signals: empty reads after read-only truncation and single-byte contents after truncating writes.
