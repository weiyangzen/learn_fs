# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/EnvTest.cpp

Purpose: Tests environment variable helper functions for setting, reading, and unsetting values, including values with spaces.

Important APIs and types: Uses `cpp-utils/system/env.h`, `std::string`, and GoogleTest.

Control flow: Tests set an environment variable, read it back, repeat with a spaced value, unset it, and verify the read result is empty.

State and persistence behavior: Mutates the process environment. Changes are process-local but can affect later tests if variable names collide or cleanup fails.

Dependencies and integration points: CLI and system utilities use environment helpers for home/config and runtime behavior.

Risks: Environment mutation is global to the process. Platform differences in unset/get semantics may matter.

Test signals: Exact value returned after set, spaced value preserved, and empty result after unset.
