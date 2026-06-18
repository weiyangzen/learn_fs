# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/UtilsTest.cpp

Purpose: This test suite verifies `cryfs-cli/program_options/utils.h`, especially `splitAtDoubleDash`, which divides CLI arguments into CryFS-owned options and passthrough options after a `--` separator.

Important APIs/types/functions: It uses `ProgramOptionsTestBase`, `splitAtDoubleDash`, and argument vectors containing short options, long options, positional options, and one or more double-dash separators. Direct tests: ProgramOptionsUtilsTest.SplitAtDoubleDash_ZeroOptions; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OneShortOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OneLongOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OnePositionalOption.

Control flow: Each `TEST_F` constructs an input vector, calls the split utility, and checks both returned vectors with `EXPECT_VECTOR_EQ`. The cases cover empty input, separator at beginning/end/middle, options on either side, and preservation of positional strings.

State and persistence behavior: The utility and tests are pure in-memory argument processing; there is no filesystem or process state.

Dependencies and integration points: The split behavior feeds CryFS CLI option parsing, where arguments before `--` are interpreted by CryFS and arguments after it are passed to lower-level mount/FUSE handling.

Risks: Incorrect separator handling can make CryFS consume FUSE options or can pass CryFS-specific flags through to the wrong layer. Edge cases around repeated or terminal separators are especially sensitive for command compatibility.

Test signals: Primary signals are ProgramOptionsUtilsTest.SplitAtDoubleDash_ZeroOptions; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OneShortOption. Assertion/mocking density: none visible.
