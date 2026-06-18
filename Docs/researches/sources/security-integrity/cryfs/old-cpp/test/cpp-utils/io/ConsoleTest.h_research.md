# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest.h

Purpose: Declares shared fixtures and async helpers for console tests. It lets tests drive an `IOStreamConsole` through pipe streams while asserting output lines and sending input lines.

Important APIs and types: Defines `ConsoleThread`, `ConsoleTest`, `print`, `EXPECT_OUTPUT_LINES`, `EXPECT_OUTPUT_LINE`, and `sendInputLine`. Uses `IOStreamConsole`, futures, threads, and `pipestream`.

Control flow: Console operations are run on a helper thread so tests can feed stdin and observe stdout in controlled order. Assertion helpers compare emitted output lines.

State and persistence behavior: State is in-memory pipes, thread/future state, and console object state. No filesystem persistence.

Dependencies and integration points: Provides the harness for ask, password, yes/no, and print console tests.

Risks: Async IO tests can deadlock if prompts or input expectations drift. The fixture must close/join threads reliably.

Test signals: Prompt output ordering, consumed input, returned answers, and no hanging helper thread.
