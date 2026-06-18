# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.c

ASCII-to-PostScript text translator.

Key responsibilities:
- Emits conforming PostScript structure, copies the `POSTPRINT` prologue, and writes setup/trailer comments.
- Translates ASCII/text input into PostScript line-printing calls.
- Expands or compresses spaces, tabs, backspaces, carriage returns, and form feeds.
- Supports font selection, line count, point size, tab stops, CR mode, page selection, copies, forms per page, orientation, offsets, accounting, copied PostScript, encoding, prologue override, and page/global requests.

Control flow:
- `main()` runs signal setup, header/prologue emission, option parsing, setup, input processing, trailer/accounting.
- `header()` pre-scans `-L` for prologue selection.
- `setup()` emits request/encoding/setup code and derives `linespp` from point size when `-l0` or negative lines are supplied.
- `arguments()` processes stdin or each named input file, starting each file on a new page.
- `text()` dispatches newlines, tabs, backspaces, spaces, formfeeds, carriage returns, and default bytes.
- `spaces()` groups runs of spaces/tabs/backspaces/CR and chooses between literal spaces or ending the string and restarting at a target column.
- `oput()` emits printable characters with PostScript escaping and optionally emits octal escapes for non-printable bytes.
- `formfeed()` closes the current page and starts the next one if input remains.

Important behavior:
- `stringcount == 1` uses fast prologue procedure `l`; multiple string/column pairs use `L`.
- `endstring()` emits `LL` chunks when too many string/column pairs accumulate, avoiding PostScript stack overflow.
- Backspacing is represented by ending the current string and restarting at an earlier column.
- Carriage return mode:
  - default ignores CR
  - mode 1 treats CR as spacing/control inside `spaces()`
  - mode 2 treats CR as newline
- Extended octal escaping is effectively always enabled by default.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `setencoding()`, `writerequest()`, `saverequest()`, `error()`, `interrupt()`.
- Local defaults and `Fontmap` from `postprint.h`.
- Expects prologue procedures `setup`, `pagesetup`, `l`, `L`, `LL`, and `done`.

Risks and quirks:
- `spaces()` uses `while ( ch = getc(fp_in) )`; EOF (`-1`) is truthy, so the loop relies on the internal `else break` path and then calls `ungetc(ch, fp_in)` even for EOF-like values.
- Page closing always emits `showpage` for the previous page, unlike `postdaisy`’s `markedpage` suppression.
- Column accounting assumes fixed-width fonts; arbitrary fonts are allowed but documented as unsuitable.
