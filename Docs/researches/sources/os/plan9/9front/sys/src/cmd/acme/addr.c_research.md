# File Research: sources/os/plan9/9front/sys/src/cmd/acme/addr.c

This file evaluates Acme address syntax over `Text` buffers.

Key responsibilities:
- `isaddrc()` identifies characters that can participate in an address.
- `isregexc()` identifies likely regex characters during click expansion.
- `nlcounttopos()` maps saved line-plus-rune offsets back into a text position, bounded by file length and line end.
- `number()` evaluates numeric line or character addresses with forward/backward/absolute direction.
- `regexp()` evaluates forward or backward regex address components using Acme's regex engine.
- `address()` parses and evaluates compound address strings including `.`, `$`, `#n`, line numbers, `+`, `-`, `/re/`, `?re?`, `,`, and `;`.

Important dependencies:
- Uses `textreadc()`, `rxcompile()`, `rxexecute()`, `rxbexecute()`, `rxnull()`, and warning reporting.
- Address evaluation operates on `Range` and accepts an arbitrary `getc` callback, so it can parse addresses from text, plumbing attributes, or command strings.

Filesystem/storage relevance:
- Address parsing is central to Acme's file interface: external clients write addresses to synthetic files like `addr` and use those ranges for `data`, `xdata`, and edit operations.

Notes:
- `;` updates the base address for the right side, matching Sam/Acme semantics.
- Empty regex reuse is guarded: no previous regex emits a warning and leaves the range unchanged.
