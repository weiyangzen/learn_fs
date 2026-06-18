# sources/user-network-fs/samba/source3/torture/test_posix_append.c

Purpose: This file is a regression test for Samba bug 6898: `GENERIC_WRITE` with POSIX semantics must not imply append-only write behavior.

Important APIs/types/functions: The single public entrypoint is `run_posix_append()`. It uses `torture_open_connection()`, `torture_setup_unix_extensions()`, `cli_ntcreate()`, `cli_writeall()`, and `cli_qfileinfo_basic()`. Access and create flags include `GENERIC_WRITE_ACCESS`, `GENERIC_READ_ACCESS`, `DELETE_ACCESS`, `FILE_FLAG_POSIX_SEMANTICS`, `FILE_OVERWRITE_IF`, `FILE_NON_DIRECTORY_FILE`, and `FILE_DELETE_ON_CLOSE`.

Control flow: The test opens file `append` with POSIX semantics and delete-on-close, writes one byte at offset zero twice, queries file size, and expects the final size to remain one byte. If the server incorrectly treats the handle as append-only, the second write extends the file to two bytes and the test fails.

State/persistence behavior: The remote file is temporary and marked delete-on-close. Persistent state is limited to file contents and size during the open handle lifetime. The test closes the connection in cleanup.

Dependencies and integration points: It depends on SMB Unix extension setup, SMB create/write/query APIs, and POSIX semantics flag handling in smbd. It is a focused protocol regression test.

Risks: Requires Unix extensions and server support for POSIX semantics. If write coalescing or file-size query behavior changes, the size assertion is the key contract. Failure leaves a delete-on-close file only if close/connection teardown also fails.

Test signals: Passing requires both writes at offset zero to succeed and `cli_qfileinfo_basic()` to report size `sizeof(c)`, not two bytes.
