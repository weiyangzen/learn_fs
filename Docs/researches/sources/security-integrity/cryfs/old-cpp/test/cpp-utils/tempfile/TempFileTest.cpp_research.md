# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileTest.cpp

Purpose: Tests `TempFile` RAII behavior across default paths, explicit paths, create-now versus do-not-create modes, readability, writability, emptiness, creatability, and deletion after use.

Important APIs and types: Uses `TempFile`, `TempDir`, fstream, GoogleTest, and helper `CreateFile`.

Control flow: Tests construct temp files under different options, inspect existence and contents, open them for reading/writing, optionally create missing files manually, and assert cleanup after scope.

State and persistence behavior: Creates real temporary files in temp directories and removes them via RAII. Explicit path tests create files under a controlled `TempDir`.

Dependencies and integration points: Used throughout tests that require filesystem-backed temporary data.

Risks: File deletion can fail with open handles. Explicit-path behavior must avoid deleting unrelated files if API is misused.

Test signals: Expected existence/non-existence, readable/writable empty file, manual creatability when not pre-created, and deletion after destructor.
