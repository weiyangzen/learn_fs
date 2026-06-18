# File Research: sources/os/plan9/9front/sys/src/cmd/idiff.c

Implements an interactive two-file merge tool driven by `diff -n`.

Key points:
- Usage: `idiff [-bw] file1 file2`.
- Rejects directories and opens both inputs as `Biobuf`s.
- Runs `/bin/diff -n`, optionally with `-b` and/or `-w`, into a temporary file.
- `parse` decodes Plan 9 diff `-n` hunk headers into source ranges and command (`a`, `c`, `d`).
- For each hunk, prints the diff, prompts for action, and writes merged output to a second temp file.
- Commands:
  - `<` keeps left side.
  - `>` takes right side.
  - `=` writes the diff hunk itself.
  - `q<`, `q>`, `q=` choose a default for remaining hunks.
  - `!cmd` runs a shell command.
- `copylines`, `skiplines`, and `copy` manage input advancement and output.
- At the end, copies merged temp output to stdout.

Dependencies and interactions:
- Uses `/bin/diff`, `/bin/rc`, Plan 9 temp-file creation with `mktemp`, and `Biobuf`.

Research relevance:
- A classic Plan 9 interactive merge utility; notable for stream-based hunk processing and direct user decisions.
