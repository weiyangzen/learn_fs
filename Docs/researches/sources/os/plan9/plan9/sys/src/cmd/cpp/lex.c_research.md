# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/lex.c

Lexer for the C preprocessor.

It encodes a compact lexical FSM, expands it into `bigfsm[256][MAXSTATE]`, and tokenizes input rows through `gettokens`. It recognizes identifiers, numbers, strings, character constants, comments, whitespace, C operators, `##`, ellipsis, trigraphs, escaped-newline folding, UTF-2/UTF-3 lead bytes in identifiers, end-of-buffer, and end-of-file sentinels.

`setsource` and `unsetsource` manage file or string input buffers; `fillbuf` grows buffers for very long input and installs sentinel bytes. `fixlex` disables `//` comments unless C++ mode is enabled.
