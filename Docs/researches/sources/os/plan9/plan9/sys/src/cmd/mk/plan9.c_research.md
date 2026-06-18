# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/plan9.c

Plan 9 platform support for `mk`.

Key areas:
- Environment import/export through `/env`.
- Process creation and shell execution with `rfork`, `fork`, pipes, and `/bin/rc`.
- Note/interrupt handling.
- File time operations and directory bulk mtime caching.
- Regex match capture copying.

Key functions:
- `readenv()` imports Plan 9 environment files as mk variables.
- `exportenv()` writes recipe environment values back to `/env`.
- `execsh()` runs shell recipes, optionally capturing output into a buffer.
- `pipecmd()` runs a shell command with optional output pipe.
- `Exit()` waits for children and exits with error.
- `catchnotes()` installs interrupt handling.
- `chgtime()` touches or creates files.
- `mkmtime()` stats files with directory-level cache warming via `bulkmtime()`.
- `rcopy()` copies regexp capture strings.

Notes:
- Shell defaults: `/bin/rc`, name `rc`.
- Uses `RFENVG` so environment changes are isolated to child copies.
