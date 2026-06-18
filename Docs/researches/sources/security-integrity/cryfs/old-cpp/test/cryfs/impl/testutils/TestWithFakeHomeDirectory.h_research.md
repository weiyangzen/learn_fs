# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/TestWithFakeHomeDirectory.h

Purpose: This fixture mixin redirects CryFS tests to a fake home directory. It isolates local-state metadata and user-specific config from the developer or CI machine.

Important APIs/types/functions: It uses cpp-utils temp directories and home-directory override helpers to install and restore a test home path.

Control flow: A fixture inherits this mixin, setup installs the fake home directory before production code resolves user paths, and teardown restores the original home behavior.

State and persistence behavior: It creates temporary filesystem state that stands in for the user's home directory. CryFS local-state files written during tests are confined there.

Dependencies and integration points: The mixin is used by config loader/creator, local-state, CLI, and filesystem tests that touch `LocalStateDir` or home-derived paths.

Risks: Failure to restore the home override could contaminate later tests; order of fixture construction matters for code that resolves paths in constructors.

Test signals: Tests can assert local-state files under the fake home path and avoid interacting with real user state.
