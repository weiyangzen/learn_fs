## sources/sync-backup/bup/lib/bup/shquote.py

Purpose: provides byte-oriented, shell-like token splitting and quoting utilities used by interactive completion and command rendering.

Important APIs and control flow: `_quotesplit()` is the state machine for quotes, backslashes, whitespace, and word offsets. `quotesplit()` returns successfully parsed `(offset, word)` tuples and suppresses `QuoteError` for unfinished input. `unfinished_word()` reports the current quote character and partial word. `quotify()`, `quotify_list()`, and `what_to_add()` render safe completions using minimal quoting.

State and dependencies: the module is stateless apart from constants `q` and `qq`; it depends only on `re`. It intentionally differs from POSIX shell parsing by dequoting only words that begin with a quote, which is important for readline completion stability.

Risks and tests: backslash handling in single quotes is deliberately narrow, and callers must not treat this as a general shell parser. Byte semantics are important; passing text strings would fail or produce incorrect regex behavior. Test coverage is likely in broader shell/completion tests outside this subset; this subset has no direct shquote test file.
