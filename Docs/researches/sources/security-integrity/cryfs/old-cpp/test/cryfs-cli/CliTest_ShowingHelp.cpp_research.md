# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_ShowingHelp.cpp

Purpose: Tests CLI help/usage display and exit behavior for long/short help options, help mixed with other options, and missing required directory arguments.

Important APIs and types: Uses `CliTest` fixture and CLI run helpers.

Control flow: Each test invokes the CLI with a specific argument set and asserts success or invalid-argument behavior plus usage output as appropriate.

State and persistence behavior: No significant filesystem state beyond fixture setup; tests focus on argument handling and output.

Dependencies and integration points: Complements parser tests by validating user-facing CLI behavior through the higher-level runner.

Risks: Help output formatting changes can break strict output checks. Mixed help/options behavior is a compatibility contract.

Test signals: Correct exit/error code and usage/help output for `--help`, `-h`, help with other args, missing all options, and missing mount dir.
