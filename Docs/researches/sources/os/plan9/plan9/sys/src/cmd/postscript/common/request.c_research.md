# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.c

Special PostScript request handling for translators.

Key responsibilities:
- Saves `-R` requests for global or per-page insertion.
- Writes matching requests at setup/page time.
- Looks up request bodies in request files and copies the selected body to output.

Important behavior:
- Request syntax is `request`, `request:page`, or `request:page:file`.
- Page `0` means global setup.
- Request file entries begin with `@name`; copied lines continue until the next `@` entry.
- Lines beginning with `#` or `%` in request bodies are skipped.

Dependencies:
- Uses `request.h`, `path.h`, `gen.h`, and `ext.h`.

Notable risks:
- Uses `strtok()` destructively on the option string.
- Keyword matching uses prefix length of `want`, so partial names can match longer request keys.
