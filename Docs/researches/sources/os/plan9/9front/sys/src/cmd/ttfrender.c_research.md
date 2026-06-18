# File Research: sources/os/plan9/9front/sys/src/cmd/ttfrender.c

This is a command-line TrueType text renderer. It reads text from a file or stdin, opens a TTF with a requested pixels-per-em, renders text to a bitmap via `ttfrender()`, optionally scales down for antialiasing, and writes a Plan 9 image to stdout.

Options control alignment/justification, target width/height, ppem, oversampling scale, newline whitespace handling, and crop mode. `elidenl()` normalizes whitespace when requested. `scaledown()` converts oversampled 1-bit render output to grayscale coverage.

`cropwrite()` trims white margins and writes a compact `k8` image. Without crop mode, output is the full rendered grayscale bitmap.
