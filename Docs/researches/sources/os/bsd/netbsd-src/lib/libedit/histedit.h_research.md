# File Research: sources/os/bsd/netbsd-src/lib/libedit/histedit.h

This is the public libedit API header for editing, history, and tokenization.

Public editing API:
- Opaque `EditLine`.
- Narrow `LineInfo`.
- Command return codes `CC_NORM` through `CC_REFRESH_BEEP`.
- Lifecycle: `el_init()`, `el_init_fd()`, `el_end()`, `el_reset()`.
- Input: `el_gets()`, `el_getc()`, `el_push()`.
- Configuration and commands: `el_set()`, `el_get()`, `el_parse()`, `el_source()`, `el_resize()`.
- Editing helpers: `el_line()`, `el_insertstr()`, `el_deletestr()`, `el_replacestr()`, `el_deletestr1()`.
- Completion helpers: `_el_fn_complete()` and `_el_fn_sh_complete()`.

Configuration constants:
- `EL_PROMPT`, `EL_TERMINAL`, `EL_EDITOR`, `EL_SIGNAL`, `EL_BIND`, `EL_TELLTC`, `EL_SETTC`, `EL_ECHOTC`, `EL_SETTY`, `EL_ADDFN`, `EL_HIST`, `EL_EDITMODE`, `EL_RPROMPT`, `EL_GETCFN`, `EL_CLIENTDATA`, `EL_UNBUFFERED`, `EL_PREP_TERM`, `EL_GETTC`, `EL_GETFP`, `EL_SETFP`, `EL_REFRESH`, `EL_PROMPT_ESC`, `EL_RPROMPT_ESC`, `EL_RESIZE`, `EL_ALIAS_TEXT`, `EL_SAFEREAD`, `EL_WORDCHARS`, and `EL_GETENV`.

Public history API:
- Opaque `History`.
- `HistEvent` with event number and string.
- `history_init()`, `history_end()`, and `history()`.
- Operation constants from `H_FUNC` through `H_NSAVE_FP`, covering navigation, add/enter/append, load/save, clear, uniqueness, deletion, data events, replacement, and file-pointer save.

Public tokenizer API:
- Opaque `Tokenizer`.
- `tok_init()`, `tok_end()`, `tok_reset()`, `tok_line()`, and `tok_str()`.

Wide-character API:
- `LineInfoW`, `HistEventW`, `HistoryW`, and `TokenizerW`.
- Wide versions of get/push/parse/set/get/line/insert/replace/history/tokenizer functions.
- `el_cursor()` for cursor movement.

Integration:
- Defines `LIBEDIT_MAJOR 2` and `LIBEDIT_MINOR 11`.
- Provides C++ linkage guards.

Risks and notes:
- The `el_set()`/`el_get()` API is varargs-heavy; callers must match the documented argument types exactly.
- Narrow and wide APIs share the same `EditLine` object, with conversion wrappers in `eln.c`.
