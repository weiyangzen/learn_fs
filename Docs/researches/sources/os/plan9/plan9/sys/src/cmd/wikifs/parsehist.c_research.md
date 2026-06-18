# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/parsehist.c

This file parses a wiki history/current file into `Whist`.

File format:
- First line is the page title.
- Then a sequence of document metadata records and body lines.
- Metadata lines begin with:
  - `D`: document timestamp.
  - `A`: author.
  - `C`: comment.
  - `X`: conflict marker.
- Body lines begin with `#`; `Brdwline` strips that marker before passing lines to `Brdpage`.

Parsing behavior:
- `Brdwhist` reads title, loops through metadata/body sections, grows `Wdoc` array by 8, parses each body with `Brdpage`, marks the latest non-conflict document as `current`, and returns a refcounted `Whist`.
- On failure, frees title, author/comment strings, parsed pages, and doc array.

Role:
- Used by `io.c` to load current/history files and by conversion/test utilities.
