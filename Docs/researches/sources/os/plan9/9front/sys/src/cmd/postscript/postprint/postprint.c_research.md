# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.c

ASCII-to-PostScript translator. It emits DSC comments, copies a prologue, applies command-line PostScript setup options, translates text into PostScript strings/operators, handles tabs/backspaces/spaces efficiently, paginates by line count, optionally filters output pages, and writes simple accounting records.

Key behavior:
- `main` runs signal setup, header/prologue emission, option parsing, setup, input processing, trailer/accounting.
- `header` pre-scans `-L` so the chosen prologue appears before setup.
- `options` supports layout, font, copies, forms-per-page, page list, offsets, font encoding, arbitrary `-P` PostScript passthrough, and common debug/ignore flags.
- `text`, `newline`, `formfeed`, `spaces`, `oput` implement the translation loop.
- `redirect` sends unselected pages to `/dev/null` based on shared `out_list`/`in_olist` helpers.

Integration points:
- Uses shared PostScript comment/path/common headers: `comments.h`, `gen.h`, `path.h`, `ext.h`.
- Requires prologue procedures `setup`, `pagesetup`, `l`, `L`, `LL`, and `done`.
- Uses shared request handling via `saverequest` and `writerequest`.

Risks:
- Classic K&R-style implicit int function definitions make portability dependent on old compiler behavior.
- `spaces` uses assignment in a `while` condition and pushes back the first non-space; NUL bytes terminate the loop path unusually.
- Page counting relies on whether `fp_out == stdout`; page filtering affects accounting semantics.
