# File Research: sources/os/plan9/9front/sys/src/cmd/acme/ecmd.c

This file implements execution of Acme/Sam-style edit commands after parsing.

Key responsibilities:
- Maintains edit execution globals: current address, nesting, current file, regex selection, and collected pipe output.
- `cmdexec()` resolves default addresses and dispatches parsed commands.
- `edittext()` is the insertion/collection entry point used by external edit-command output.
- `filelist()` supports command file-list arguments, including collection from `<` pipes.
- Implements edit commands:
  - `a`, `i`, `c`, `d` for insert/change/delete through edit logs.
  - `e`/`r` for reading files into ranges.
  - `f` for setting/printing file names.
  - `g`/`v`, `x`/`y`, `X`/`Y` for regex/file looping.
  - `m`/`t` for move/copy.
  - `s` substitution with `&` and numeric submatch replacements.
  - `u` undo/redo.
  - `w` writing ranges to disk.
  - `<`, `|`, `>` pipe integration.
  - `=`, newline, `p`, `b`, `B`, `D`.
- `runpipe()` invokes shell commands in edit mode and coordinates with `cedit`.
- Address support includes `cmdaddress()`, `charaddr()`, `lineaddr()`, `nextmatch()`.
- File matching helpers resolve explicit files and regex-matched file names.
- `cmdname()` computes and optionally sets file names, with duplicate-name warnings.

Important dependencies:
- Relies on `edit.c` parse trees (`Cmd`, `Addr`, `String`) and `cmdtab`.
- Uses `elog.c` to defer and apply modifications safely.
- Uses `exec.c` for external commands and `look.c` path helpers.
- Uses `regx.c` for regex execution.

Filesystem/storage relevance:
- Reads files (`open`, `dirfstat`, `loadfile`), writes files through `putfile()`, and invokes external commands through Acme's mounted 9P namespace.
- Protects writes when a file has pending modifications in the current sequence.

Notes:
- Edit changes are logged before application so addresses refer to the original buffer state.
- `X`/`Y` file loops temporarily add references to all windows to keep targets alive during cross-window editing.
