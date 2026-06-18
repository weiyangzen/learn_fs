# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPathParseTools.hh

## Purpose
Provides small path/string tokenization helpers used by resource-monitor code to map LFNs onto directory-state trees without pulling in heavier parser dependencies.

## Important APIs, Types, and Functions
- `SplitParser`: owns a duplicated mutable string and tokenizes it with C delimiter functions.
- `get_token()`, `get_token_as_string()`, `get_reminder()`, and `get_reminder_with_delim()` expose token stream and remaining suffix.
- `pre_count_n_tokens()` counts remaining tokens for reserve sizing.
- `PathTokenizer`: private `SplitParser` subclass that extracts directory components and a remainder from a path.
- `PathTokenizer::make_path()` reconstructs a slash-prefixed path from parsed components.

## Control Flow
`PathTokenizer` initializes a delimiter parser over `/`, optionally caps directory extraction by `max_depth`, optionally treats the last token as file remainder for LFNs, and stores pointers into the duplicated string. Consumers query directory count and individual directory names.

## State and Persistence Behavior
No persistent state. The tokenizer stores pointers into `SplitParser::f_str`; those pointers remain valid only while the tokenizer object lives.

## Dependencies and Integration Points
Uses only C/C++ standard string/vector and `strdup`/`free`/`strspn`/`strpbrk`. It integrates with `ResourceMonitor` and `DirState` path lookup logic.

## Risks and Test Signals
Risks include the misspelled `get_reminder` API, pointer lifetime misuse, mutation of delimiter characters, and behavior with repeated/trailing slashes. Tests should cover root path, repeated separators, max depth, parse-as-LFN true/false, and reconstructing paths.
