# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/Opostdaisy.c

Diablo 1640-to-PostScript translator, apparently an older or alternate copy of `postdaisy.c`.

Key responsibilities:
- Emits Adobe structuring comments, copies the `POSTDAISY` prologue, optionally includes round-page support, and writes setup/trailer sections.
- Parses Diablo printer text controls into positioned PostScript text calls.
- Maintains printer state: horizontal/vertical position, margins, HMI/VMI spacing, tabs, page counters, reverse-printing mode, CR/LF behavior, and auto-bold state.
- Handles page selection through `out_list()`/`in_olist()`, page requests through `writerequest()`, form-per-page setup, accounting, and font encoding.
- Supports font aliases through `Fontmap` and maps short names like `R`, `I`, `B`, `CO`, `CI`, and `CB`.

Input/control flow:
- `main()` runs signal setup, header/prologue emission, option parsing, setup, file arguments, trailer/accounting.
- `text()` processes each input byte and dispatches backspace, tab, newline, vertical tab, formfeed, carriage return, escape sequences, and printable characters.
- `escape()` implements Diablo escape commands for margins, tabs, horizontal/vertical motion, line count, CR/LF modes, reverse printing, auto underscore, bold/shadow printing, and several ignored escape families.
- `formfeed()` closes the current page, suppresses some trailing blank pages using `markedpage`, and starts the next page if input remains.
- `oput()` emits character data into PostScript string chunks and tracks string start, last character, last horizontal position, line state, and reverse advance.

Important behavior:
- Output strings are chunked when `stringcount > 100` to avoid excessive PostScript stack use.
- Backward print mode moves before emitting a character, then suppresses normal forward motion.
- Duplicate overstrikes of the same character at the same position are suppressed by `lastc`/`prevx`.
- `changefont()` ends the active line before emitting a PostScript `f` font change.
- `redirect()` sends unselected pages to `/dev/null`.

Notable differences from `postdaisy.c`:
- Does not include the Plan 9 `isascii()` compatibility definition or `<sys/types.h>`.
- Declares `int interrupt()` locally in `init_signals()`.
- In `text()`, only ASCII printable default characters reach `oput()`.
- In `oput()`, output characters are written directly after escaping `\`, `(`, and `)`; non-printable/non-ASCII octal escaping is not present.

Dependencies:
- Uses shared PostScript support headers and globals from `comments.h`, `gen.h`, `path.h`, `ext.h`, and common objects such as `glob.o`, `misc.o`, and `request.o`.
- Expects PostScript prologue procedures `setup`, `pagesetup`, `t`, `f`, and `done`.

Risks and quirks:
- `cleartabs()` iterates `ROWS` over `htabstops[COLUMNS]`, which can write past the horizontal tab array.
- `htab()` scans up to `ROWS` while indexing `htabstops`, another possible out-of-bounds read.
- Several tab and margin indices use divisions like `hpos/ohmi` and `vpos/ovmi` without bounds checks.
- Escape command `'\015'` sets `leftmargin = BOTTOMMARGIN`, likely a typo for `LEFTMARGIN`.
- Comments explicitly say reverse printing, tabs, page comments, and some Diablo behavior are not well tested.
