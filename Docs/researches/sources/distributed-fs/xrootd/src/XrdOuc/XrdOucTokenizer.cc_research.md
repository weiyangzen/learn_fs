# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.cc

Purpose: implements an in-place tokenizer for caller-owned character buffers, providing line extraction, blank-delimited tokens, optional lowercasing, tab handling, and one-token rollback.

Important APIs, types, and functions: `Attach()` resets the tokenizer to a buffer. `GetLine()` returns the next line after trimming leading blanks and optionally tabs, replacing the line terminator with null. `GetToken()` returns the next blank-delimited token and optionally the rest of the line. `RetToken()` restores the previous token boundary once.

Control flow: `GetLine()` advances `buff` over newline-separated records and sets `tnext` to the current line start. `GetToken()` skips spaces from `tnext`, lowercases if requested while scanning, null-terminates the token, advances `tnext`, and fills `rest` after skipping spaces. `RetToken()` changes the token's trailing null back to a space when possible and resets the cursor.

State and persistence: state is four fields pointing into the caller's mutable buffer plus a tab-conversion flag. The tokenizer does not allocate or persist data and modifies the input buffer destructively.

Dependencies and integration points: depends on C ctype/string headers and the declaration header. It is a lower-overhead counterpart to `XrdOucStream` for tokenizing existing memory.

Risks and test signals: the `Tabs()` comment says `0` converts tabs, but implementation converts tabs when `notabs` is true, set by `Tabs(0)`. Leading tabs are only skipped in that mode. Tests should cover empty buffers, trailing lines without newline, tabs on/off, rollback after end-of-line, `rest` behavior, and lowercasing.
