# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskYesNo.cpp

Purpose: Tests yes/no console prompt parsing. It accepts uppercase/lowercase `yes`, `y`, `no`, and `n`, trims surrounding spaces, rejects empty input, and reprompts after wrong input.

Important APIs and types: Uses helper macros/functions `EXPECT_TRUE_ON_INPUT`, `EXPECT_FALSE_ON_INPUT`, and `EXPECT_RESULT_ON_INPUT` from the console test fixture.

Control flow: Each test starts a yes/no prompt, feeds one or more input lines, and asserts the returned boolean. Invalid input tests verify retry behavior before success.

State and persistence behavior: Only pipe-backed console state and async result futures are used.

Dependencies and integration points: Supports CLI confirmation flows that depend on robust parsing and predictable prompts.

Risks: Locale or alternative yes/no strings are not covered. Tests are sensitive to prompt/read ordering.

Test signals: Boolean result for accepted forms, whitespace trimming, retry after bad input, and no hanging async prompt.
