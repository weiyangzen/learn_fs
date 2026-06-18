# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/FiletimeTest.cpp

Purpose: Tests file timestamp get/set helpers by applying a known time to a temporary file and reading it back.

Important APIs and types: Uses `cpp-utils/system/filetime.h`, `TempFile`, platform `timespec` handling, and GoogleTest.

Control flow: Creates a temp file, sets its modification/access time, retrieves it, and compares expected timestamp fields.

State and persistence behavior: Mutates metadata of a temporary file that is cleaned up after the test.

Dependencies and integration points: Timestamp helpers are relevant for filesystem metadata preservation and platform abstraction.

Risks: Filesystem timestamp precision differs by platform and filesystem. Tests must account for truncation/rounding.

Test signals: Retrieved timestamp equals the expected time within the semantics encoded by the helper.
