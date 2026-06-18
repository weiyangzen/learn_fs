# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/FakeCryKeyProvider.h

Purpose: This header defines a fake `CryKeyProvider` for config-file tests. It supplies deterministic key material without prompting a console or running a real password flow.

Important APIs/types/functions: It depends on the CryFS key-provider interface and cpp-utils data/key types. The fixture exposes a simple provider object whose request methods return preconfigured keys.

Control flow: Tests instantiate the fake provider, pass it into `CryConfigFile` or encryptor helpers, and then load/create encrypted configs using stable key bytes.

State and persistence behavior: The provider stores only in-memory key data. Persistence happens in the config files under test, not in the helper itself.

Dependencies and integration points: It integrates config-file encryption/decryption tests with the production key-provider abstraction while avoiding console/KDF costs.

Risks: Because it bypasses password prompts and KDF behavior, it should only be used where deterministic key material is the point of the test.

Test signals: Callers observe successful config encryption/decryption with the expected key and failure when a different key provider is used.
