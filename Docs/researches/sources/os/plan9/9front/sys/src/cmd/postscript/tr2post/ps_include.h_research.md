# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.h

Static PostScript wrapper fragments for `ps_include.c`. `PS_head` saves state, disables page operators, creates an inclusion dictionary, and captures the operand stack. `PS_setup` computes bounding box transforms, clipping, scaling, rotation, whiteout, and outline variables. `PS_tail` restores graphics/interpreter state and optionally outlines the included box.

Integration points:
- Included directly by `ps_include.c`.
- Arrays are null-terminated and emitted string-by-string.

Risks:
- PostScript code is embedded as C string arrays, making syntax validation manual.
- Wrapper intentionally neutralizes page operators, which may affect unusual included PostScript that depends on them.
