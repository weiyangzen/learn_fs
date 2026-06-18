# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirTest.cpp

Purpose: Tests `TempDir` RAII behavior: directory creation, initial emptiness, writability, and deletion after scope exit.

Important APIs and types: Uses `TempDir`, fstream, GoogleTest, and helper functions to count entries and create files.

Control flow: Tests construct a `TempDir`, inspect its path, create files inside it, verify write access, then leave scope and assert deletion.

State and persistence behavior: Creates real temporary directories and files, then relies on RAII cleanup to remove them.

Dependencies and integration points: Many tests use temporary directories for safe filesystem state isolation.

Risks: Cleanup can fail due to open handles or permissions, especially on Windows. Counting entries can be platform-sensitive if hidden/system files appear.

Test signals: Directory exists, starts empty, accepts writes, and no longer exists after destructor.
