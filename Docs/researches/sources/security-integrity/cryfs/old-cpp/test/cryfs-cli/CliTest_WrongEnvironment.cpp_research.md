# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_WrongEnvironment.cpp

Purpose: Tests CLI behavior in invalid filesystem environments, especially permission combinations and environment variables. It defines table-driven helpers for success/error expectations.

Important APIs and types: Uses `CliTest`, `cpp-utils/system/env.h`, local `TestConfig`, permission helpers `SetAllPermissions`, `SetNoReadPermission`, `SetNoWritePermission`, `SetNoExePermission`, `SetNoPermission`, and helper tests `Test_Run_Success`/`Test_Run_Error`.

Control flow: The suite constructs configurations for basedir/mountdir/log/config paths, changes permissions, sets environment values when needed, runs the CLI, and asserts success or error.

State and persistence behavior: Mutates real temp directory permissions and process environment. Cleanup/restoration is critical for isolation.

Dependencies and integration points: Exercises OS permission handling, CLI validation, and environment-dependent setup.

Risks: Permission tests are platform- and user-sensitive, especially if run as root or on Windows. Global environment changes can leak.

Test signals: Expected CLI success/error for each permission/config matrix and correct restoration after tests.
