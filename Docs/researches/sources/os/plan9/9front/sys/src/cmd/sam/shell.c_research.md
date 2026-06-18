# File Research: sources/os/plan9/9front/sys/src/cmd/sam/shell.c

`shell.c` implements sam's `!`, `<`, `>`, `|`, `^`, and `_` Plan 9 command integration.

`plan9` stores/reuses the last shell command, sets up error capture in downloaded mode, creates pipes based on command type, forks `/bin/rc -c`, optionally pipes selected text into the command, reads command output into the file or command buffer, writes selected text to command stdin, and reports status.

For filter commands (`|`, `_`), it first snarfs the addressed text into `plan9buf`, then a child writes that buffer to a pipe feeding the shell. For insertion/replacement commands (`<`, `|`), it deletes selected text and reads command output through `readio`.

`updateenv` sets `%` and `%dot` environment variables for shell commands, describing current filename and dot range. `checkerrs` displays the first few stderr lines from the sam error file and points to the file if more remains.

`cmdbuf` and `cmdbufpos` support `^` and `_` commands that feed generated command text back into sam's command parser.
