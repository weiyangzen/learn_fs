# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/daemonize_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/process/daemonize.h`.

Important APIs and types: Includes daemonization public header.

Control flow: No runtime daemonization is performed.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards CLI/process code that includes daemonization helpers.

Risks: Does not validate fork/session/stdout behavior, only header self-containment.

Test signals: Successful compilation.
