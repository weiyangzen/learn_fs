# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.hh

Purpose: declares a simple destructive tokenizer for mutable memory buffers.

Important APIs, types, and functions: constructor calls `Attach()`. Public methods are `Attach()`, `GetLine()`, `GetToken()`, `RetToken()`, and `Tabs()`. Private fields track the input buffer, last token, next token cursor, and tab conversion flag.

Control flow: users attach a mutable buffer, iterate lines, then tokens within a line. One call to `RetToken()` can push back the last returned token.

State and persistence: all parser state points into the caller-provided buffer and is invalid if that buffer is freed or replaced. No data is persisted.

Dependencies and integration points: the header is standalone and integrates with configuration or protocol parsing code that can safely mutate its input.

Risks and test signals: because tokenization writes null bytes into the source, callers must not pass string literals or shared immutable buffers. Tests should compile the header standalone and verify object reuse through `Attach()`.
