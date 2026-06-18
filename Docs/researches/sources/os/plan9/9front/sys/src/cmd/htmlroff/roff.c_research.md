# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/roff.c

Implements the central `htmlroff` roff dispatcher, input loop, paragraph generation, escape handling, and output emission.

Key points:
- Maintains fixed tables for regular requests, raw requests, and escape handlers.
- Provides `addreq`, `delreq`, `renreq`, `addraw`, `delraw`, `renraw`, and `addesc`.
- `getnext` fetches logical input characters, expanding registered escapes depending on input mode and handling formatted diversion markers.
- `_readx`, `copyarg`, `readline`, and `parseargs` parse request arguments and lines under different expansion/copy modes.
- `dotline` dispatches dot/tick requests to raw handlers, regular handlers, or user-defined macros.
- `newline`, `startoutput`, and `br` translate roff line/paragraph state into styled HTML paragraph tags.
- `runinput` is the main loop: detects requests at beginning of line, handles newlines/traps, starts output, shows inline tags, and writes characters/tabs.
- `run` initializes all supported section modules, registers extra `margin`, sets defaults, runs input, invokes EOF macro, and closes HTML tags.
- `outrune` maps private sentinels to HTML-safe output, handles non-fill spaces, plus/equal/minus symbol output, prime as superscript, and optional diversion callback.
- Includes no-op/warning request and escape handlers for unsupported features.

Dependencies and interactions:
- Calls every `t*.c` initializer, `htmlinit`, input-stack functions, macro functions, register functions, and HTML output functions.
- `t9init` and `t12init` are commented out in `run`, so tabs/fields and drawing/overstrike escapes are not active despite `t12.c` existing.

Research relevance:
- This is the core interpreter loop and output engine for `htmlroff`; most section modules register behavior into this dispatcher.
