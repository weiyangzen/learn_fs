# File Research: sources/os/plan9/9front/sys/src/cmd/sam/xec.c

`xec.c` executes parsed sam commands. `cmdexec` applies default addresses, resolves address expressions, loads unread files as needed, sets `curfile`, and dispatches to the command function from `cmdtab`.

It implements editing commands (`a`, `c`, `d`, `i`, `m`, `t`, `s`), file/menu commands (`b`, `B`, `D`, `e`, `f`, `n`, `w`, `q`, `cd`), display/address commands (`p`, newline, `=`), mark/undo commands (`k`, `u`), regex conditional/looping commands (`g`, `v`, `x`, `y`, `X`, `Y`), Plan 9 shell commands, and custom terminal menu command updates (`M`).

`append`, `display`, `move`, and `copy` perform the concrete text operations via `loginsert`/`logdelete`.

` s_cmd` handles substitution with `&` and `\1`-`\9` submatch expansion, global substitution, empty-match avoidance, and dot update.

`looper`, `linelooper`, and `filelooper` implement regex range iteration, line iteration, and file-list iteration with nesting guards and current-file restoration.
