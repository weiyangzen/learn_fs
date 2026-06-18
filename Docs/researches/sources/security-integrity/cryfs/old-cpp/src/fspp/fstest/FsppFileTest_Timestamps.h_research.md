# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest_Timestamps.h

Purpose: timestamp-specific tests for `fspp::File` operations before an `OpenFile` is used. It verifies open operations do not affect timestamps and file-level truncation updates mtime and ctime.

Important APIs/types/functions: `FsppFileTest_Timestamps`, `CreateFileWithSize`, `open(fspp::openflags_t)`, `truncate`, and timestamp expectation helpers from `TimestampTestUtils`.

Control flow: helper creates a file and optionally truncates it to a known size. Each typed test returns a move-capturing operation closure and evaluates expected timestamp deltas under all atime configurations.

State and persistence behavior: the file size is set through `File::truncate` and verified via `Load(path)->stat`. Tests compare metadata around operations rather than content bytes.

Dependencies and integration points: relies on `TimestampTestUtils`, `FileSystemTest::CreateFile`, `Load`, `stat`, and fspp open-flag constructors. Registered as a typed suite for concrete filesystem implementations.

Risks and test signals: establishes that open is metadata-neutral for no mode, read-only, write-only, and read-write flags. Truncation expectations update mtime/ctime even when truncating zero to zero, which may intentionally encode CryFS semantics but differs from some filesystem optimizations.
