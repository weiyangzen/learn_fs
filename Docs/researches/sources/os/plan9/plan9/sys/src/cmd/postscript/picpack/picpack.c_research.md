# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.c

Troff preprocessor that packs referenced picture files inline.

Key responsibilities:
- Scans input for picture request macros, default `.BP` and `.PI`.
- Copies each referenced picture file once into troff transparent mode output.
- Emits `x X InlinePicture filename bytes` device-control records.
- Performs a second pass to copy the original input after inline picture payloads.
- Supports custom key strings, quiet mode, debug, and ignore-fatal flags.
- Copies stdin to a temporary file so it can be scanned twice.

Important behavior:
- Picture names are parsed as the second token and truncated at `(`.
- Transparent output prefixes lines with `\!` and escapes backslashes.
- A temp file records already-added picture filenames.

Dependencies:
- Uses common `gen.h`, `ext.h`, `path.h`, and `tempnam()`.

Notable risks:
- Fixed line/name buffers can truncate long input lines or pathnames.
- Duplicate tracking repeatedly opens the temp file.
- `tempnam()`-style temp creation is race-prone.
