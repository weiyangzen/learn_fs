# sources/storage-engines/sqlite/tool/Replace.cs

## Purpose
`Replace.cs` is a C# standard-input filter that applies a regular expression replacement to each input line and writes either all transformed lines or only lines that changed. It is suitable for build pipelines and source-generation scripts needing regex substitutions without platform-specific shell tools.

## Important APIs, Types, and Functions
`ExitCode` captures argument, boolean parse, exception, and success outcomes. `Replace.Error()` prints usage and diagnostics. `Main()` constructs `Regex` from the first argument, uses the second argument as replacement, parses the third argument as `matchingOnly`, then loops over `Console.In.ReadLine()` and writes to `Console.Out`.

## Control Flow
The tool requires exactly three arguments: pattern, replacement, and a Boolean `matchingOnly` flag. For each input line it calls `regEx.Replace()`. When `matchingOnly` is false, every output line is written. When true, only lines whose replacement output differs by ordinal comparison are emitted.

## State and Persistence
The program has no persistent state and does not touch files directly. State is limited to the compiled `Regex`, replacement string, parsed flag, and one line at a time from stdin.

## Dependencies and Integration Points
The file uses `System.Text.RegularExpressions`, `System.IO`, `System.Diagnostics`, reflection metadata, and standard console streams. It integrates as a command-line build helper with numeric exit codes.

## Risks
User-supplied regex patterns can be expensive and there is no timeout, so catastrophic backtracking can stall a pipeline. Regex construction exceptions are caught and reported as generic `Exception`. Line-oriented processing means it cannot match across newline boundaries and preserves platform default console encoding behavior.

## Test Signals
Exercise replacements with and without matches, `matchingOnly=true` and `false`, invalid Boolean values, invalid regex syntax, empty input, replacement group syntax, and large inputs to confirm streaming behavior.
