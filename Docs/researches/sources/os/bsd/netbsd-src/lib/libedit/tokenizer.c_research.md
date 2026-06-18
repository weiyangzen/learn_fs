# File Research: sources/os/bsd/netbsd-src/lib/libedit/tokenizer.c

## Purpose
Implements Bourne-shell-like tokenization for libedit. The file is compiled twice: once for narrow `char` APIs and once for wide `wchar_t` APIs.

## Main Components
- Macro layer maps `Char`, function names, string functions, and type names based on `NARROWCHAR`.
- `struct tokenizer` stores IFS characters, argv array, word buffer, quote state, and tokenizer flags.
- Quote states distinguish no quote, single quote, double quote, one-character escape, and one-character escape inside double quotes.
- `tok_init` / `tok_winit` allocate tokenizer state, argv storage, IFS copy, and word buffer.
- `tok_reset` / `tok_wreset` clears reusable parse state.
- `tok_end` / `tok_wend` frees tokenizer allocations.
- `tok_line` / `tok_wline` parses `LineInfo`, preserving cursor-to-argument mapping and reporting unmatched quote states.
- `tok_str` / `tok_wstr` tokenizes NUL-terminated strings by constructing a temporary line-info view.

## Integration
Used by libedit consumers through `histedit.h` tokenizer APIs. It supports completion and command parsing by returning argc/argv plus cursor argument and offset.

## Risks / Notes
Manual realloc growth updates stored argv pointers when the word buffer moves. Return codes distinguish internal error, quoted continuation, unmatched double quote, unmatched single quote, and success.
