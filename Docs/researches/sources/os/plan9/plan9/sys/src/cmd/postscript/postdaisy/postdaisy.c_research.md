# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.c

Diablo 1640-to-PostScript translator, updated from `Opostdaisy.c` for Plan 9 and binary-safe character emission.

Key responsibilities:
- Emits conforming PostScript job structure, copies the `POSTDAISY` prologue, writes setup/trailer comments, and supports multiple forms per sheet.
- Translates Diablo 1640 text and motion controls into positioned PostScript strings handled by the prologue `t` procedure.
- Tracks horizontal/vertical motion, margins, tabs, page boundaries, CR/LF modes, reverse printing, automatic underline, and bold/shadow mode.
- Parses command-line options for aspect ratio, copies, font, HMI/VMI, lines per page, magnification, page list, orientation, offsets, accounting, copied PostScript snippets, encoding, prologue, and requests.

Input/control flow:
- `header()` pre-scans only for `-L` so the selected prologue can be copied before setup options are emitted.
- `options()` mutates translator state and emits PostScript definitions.
- `arguments()` translates stdin or each named input file through `text()`.
- `text()` starts with a dummy redirected page, initializes tabs, and dispatches input bytes to motion/control handlers.
- `escape()` implements Diablo escape sequences for margins, tabs, motion indexes, CR/LF policy, absolute column/line movement, half-line motion, font changes, and unimplemented graphics modes.
- `oput()` handles line/string chunking, character escaping, reverse printing, duplicate overstrike suppression, and page marking.

Important behavior:
- For ordinary bytes, `text()` calls `oput(ch)` unconditionally in the default case.
- `oput()` emits ASCII printable bytes directly, escaping PostScript string metacharacters, and emits other bytes as three-digit octal escapes.
- `formfeed()` increments `printed` only when current output is stdout, allowing page selection to suppress accounting for skipped pages.
- `ungetc(getc(fp_in), fp_in)` is used to decide whether another page should be started.
- `markedpage` suppresses trailing blank-page `showpage` for some jobs.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `writerequest()`, `setencoding()`, `saverequest()`, `error()`, `interrupt()`.
- Local constants and `Fontmap` come from `postdaisy.h`.
- Expects prologue procedures `setup`, `pagesetup`, `t`, `f`, `done`, and optionally form setup procedures.

Risks and quirks:
- Same tab array problems as `Opostdaisy.c`: `cleartabs()` writes `ROWS` entries to `htabstops[COLUMNS]`, and `htab()` scans with the wrong upper bound.
- Escape commands index tab arrays without validating computed columns/lines.
- `leftmargin = BOTTOMMARGIN` in the “clear all margins” escape case looks wrong.
- Error handling for malformed multi-byte escape sequences does not check EOF before using `getc()` results.
- The source comments state graphics mode is not implemented and reverse-printing behavior is untested.
