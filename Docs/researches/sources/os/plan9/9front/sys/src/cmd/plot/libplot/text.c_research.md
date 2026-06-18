# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/text.c

`text.c` draws plot text at the current pen position. It parses leading `\C`, `\R`, and `\L` alignment modifiers, splits lines on `\n`, converts coordinates, calls `m_text()`, and advances the current y position for multi-line text.
