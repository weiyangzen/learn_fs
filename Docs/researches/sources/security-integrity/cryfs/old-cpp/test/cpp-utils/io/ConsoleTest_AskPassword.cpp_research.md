# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskPassword.cpp

Purpose: Tests password prompt input handling for non-empty and empty passwords.

Important APIs and types: Uses `ConsoleTest` and the console password prompt API. The fixture controls stdin/stdout through pipe streams.

Control flow: The test starts the password prompt asynchronously, sends an input line, and asserts the returned password string.

State and persistence behavior: Password data exists only in memory during the test. No files are written.

Dependencies and integration points: Covers CLI credential-entry behavior at the console abstraction boundary. Echo-disabling behavior is covered elsewhere.

Risks: These tests validate returned strings but not terminal echo state on real TTYs. Empty password acceptance is an explicit behavioral contract.

Test signals: Returned password matches input for ordinary and empty input without deadlock.
