# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Ask.cpp

Purpose: Tests multi-option console prompts. It verifies option rendering, numeric selection, whitespace trimming, empty input handling, out-of-range numbers, and non-numeric retry behavior.

Important APIs and types: Uses `ConsoleTest` fixture and `IOStreamConsole::ask`-style behavior through helper methods.

Control flow: Each test starts an ask call, checks prompt output, sends one or more input lines, and asserts the returned selected option. Invalid input tests verify reprompt loops.

State and persistence behavior: State is pipe-backed stdin/stdout and the pending async console operation. No persistent state.

Dependencies and integration points: Integrates the console abstraction with user-facing CLI prompt behavior.

Risks: Text formatting and input parsing are tightly coupled to CLI UX. Tests can hang if a reprompt is missing or expected input is not consumed.

Test signals: Correct selected index/value, output line content, whitespace tolerance, crash/throw for no options, and recovery after invalid input.
