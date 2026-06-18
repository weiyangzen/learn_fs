# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/random/RandomIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/random/Random.h`.

Important APIs and types: Includes the public random helper header.

Control flow: No runtime random generation is performed.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards users of random utilities, including crypto/test fixture code that may include the header directly.

Risks: Does not validate entropy quality or deterministic behavior.

Test signals: Successful direct header compilation.
