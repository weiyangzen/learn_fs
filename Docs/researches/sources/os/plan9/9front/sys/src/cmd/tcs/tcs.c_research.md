# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/tcs.c

`tcs.c` is the main driver for the Plan 9 character set conversion command.

Main behavior:
- Parses `-f from`, `-t to`, `-l`, `-c`, `-s`, and `-v`.
- Defaults to UTF input and UTF output.
- Resolves charset names through `aliasname()` and `conv()`.
- Converts stdin or each named file through either table-driven or function-driven converters.
- Tracks `ninput`, `nrunes`, `noutput`, and `nerrors`.

Core paths:
- `main()` selects input and output `struct convert` entries and dispatches each file.
- `list()` prints available character sets from `convert[]`.
- `intable()` maps each input byte through a 256-entry table to `Rune`.
- `outtable()` builds an inverse byte map from a 256-entry Unicode table and writes single-byte output.
- `unicode_in*()` and `unicode_out*()` handle UTF-16-like “unicode” big/little endian input/output, including BOM processing.
- `fixsurrogate()` combines surrogate pairs into runes.

Important data:
- Includes many charset data headers: Cyrillic, ISO-8859, Microsoft/OEM, Big5, GB, etc.
- Defines `convert[]`, the central registry of supported charsets and aliases.
- Table charsets use `Table`; stateful/multibyte charsets use function pairs.

Risk notes:
- `unicode_in()` has a deliberate `default: OUT(out, &r, 1);` fallthrough into little-endian processing; this treats the first non-BOM word as data then continues.
- `outtable()` rebuilds the inverse map on every call, which is simple but repeated work for large output streams.
- Error handling depends on `squawk` and `clean`: invalid input/output chars can warn, count errors, drop chars, or map to `BADMAP`.
