# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockCryKeyProvider.h

Purpose: This header defines a Google Mock implementation of the CryFS key-provider interface. It lets tests assert exactly when new or existing filesystem keys are requested and which key data is returned.

Important APIs/types/functions: It mocks `CryKeyProvider` methods for new and existing filesystems and uses cpp-utils data/key types in return values.

Control flow: Tests configure `EXPECT_CALL` on the mock provider, execute config loading or encryption code, and verify the key request path taken by the production component.

State and persistence behavior: The mock stores expectation state only. Any persistent effects come from config files that receive the mocked key material.

Dependencies and integration points: It integrates key-provider contract tests with `CryConfigFile`, config loaders, and encryptor factories.

Risks: It verifies interaction shape rather than cryptographic strength; tests that need real KDF coverage should use password-based providers instead.

Test signals: Google Mock call counts, selected provider method, and returned key bytes drive pass/fail behavior.
