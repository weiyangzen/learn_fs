# File Research: sources/os/plan9/9front/sys/src/cmd/acme/exec.c

This file implements Acme tag commands, command execution, snarf/cut/paste, file Get/Put, process launching, and command argument handling.

Key responsibilities:
- Defines `exectab`, mapping tag command names (`Cut`, `Del`, `Dump`, `Edit`, `Get`, `Put`, `Undo`, `Zerox`, etc.) to functions and flags.
- `execute()` expands clicked text, sends events to external clients when appropriate, runs built-in commands, or launches external commands.
- Argument helpers `getarg()`, `getbytearg()`, `getname()`, and `printarg()` collect selected/file/address arguments.
- Window/layout commands: `newcol()`, `delcol()`, `del()`, `sort()`, `zeroxx()`.
- File commands:
  - `get()` reloads file content while preserving selections by line/rune coordinates when the same name is reloaded.
  - `putfile()` writes buffer ranges to disk, checks qid/dev/mtime to avoid overwriting externally modified files, rejects append-only files, updates clean state, and sends plumber `put` messages.
  - `put()`, `putall()`, `dump()`.
- Editing commands: `cut()`, `paste()`, `sendx()`, `edit()`, `undo()`.
- Search and view commands: `look()`, `fontx()`, `incl()`, `indent()`, `tab()`, `id()`, `local()`, `kill()`, `exit()`.
- `runproc()`, `runwaittask()`, and `run()` create child processes, mount Acme's namespace for them, wire stdin/stdout/stderr to Acme files depending on pipe command form, and notify the wait thread.

Important dependencies:
- Uses almost every Acme subsystem: text/file/window/layout, fsys mounting, plumber, snarf, edit parser, row dump/load, font cache.
- External execution mounts `/mnt/acme`, binds it to `/mnt/wsys` and `/dev`, sets `winid`, `%`, and optionally `acmeaddr`.

Filesystem/storage relevance:
- Major file-facing code:
  - Reads and reloads files/directories.
  - Writes Acme buffers back to disk with external-modification checks.
  - Exposes selected text and command I/O through synthetic files like `rdsel`, `wrsel`, and `editout`.
  - Uses plumber messages for close/put events.

Notes:
- `runproc()` chooses direct `procexec` for simple commands and falls back to `/bin/rc -c` for shell syntax.
- For edit commands using pipes, stdout can be directed into window `editout` to feed `edittext()`.
