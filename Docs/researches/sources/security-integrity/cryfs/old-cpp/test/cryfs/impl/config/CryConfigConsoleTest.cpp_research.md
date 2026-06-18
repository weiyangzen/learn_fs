# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigConsoleTest.cpp

Purpose: This file tests the interactive/noninteractive console layer that chooses ciphers, block sizes, and missing-block integrity policy during config creation.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, cryfs/impl/config/CryConfigConsole.h, cryfs/impl/config/CryCipher.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/io/NoninteractiveConsole.h, ../../impl/testutils/MockConsole.h. Classes/fixtures: CryConfigConsoleTest, CryConfigConsoleTest_Cipher, CryConfigConsoleTest_Cipher_Choose. Helper functions: CryConfigConsoleTest, EXPECT_DONT_SHOW_WARNING, EXPECT_SHOW_WARNING. Direct tests: CryConfigConsoleTest_Cipher.AsksForCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipherWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher.AsksForBlocksize; CryConfigConsoleTest_Cipher.AsksForMissingBlockIsIntegrityViolation; CryConfigConsoleTest_Cipher.ChooseDefaultBlocksizeWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher_Choose.ChoosesCipherCorrectly.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is mock-console expectation state plus chosen config values returned from console helper methods. No config file is persisted directly here.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Exact prompt flow can be brittle, but the brittleness is useful because these prompts are user-facing setup contracts.

Test signals: Primary signals are CryConfigConsoleTest_Cipher.AsksForCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipherWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher.AsksForBlocksize; CryConfigConsoleTest_Cipher.AsksForMissingBlockIsIntegrityViolation; CryConfigConsoleTest_Cipher.ChooseDefaultBlocksizeWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher_Choose.ChoosesCipherCorrectly. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x14.
