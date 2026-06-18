# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/subprocess_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/process/subprocess.h`.

Important APIs and types: Includes the public subprocess helper header.

Control flow: No runtime subprocess is launched in this file.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects consumers of subprocess utilities from hidden include-order dependencies.

Risks: Does not validate execution semantics; `SubprocessTest.cpp` provides behavioral coverage.

Test signals: Successful compilation.
