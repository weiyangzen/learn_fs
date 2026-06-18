# File Research: sources/os/plan9/plan9/sys/src/cmd/p.c

Implements a minimal pager. It prints input in chunks of `pglen` lines, defaulting to 22 lines, and waits for commands from `/dev/cons` between chunks.

Arguments beginning with `-` set page length; file arguments are opened and paged sequentially. With no file arguments, stdin is paged.

At prompts, `q` or EOF exits. Commands beginning with `!` are run through `/bin/rc -c` with console input attached, after which the pager prompts again. Long lines that exceed `Brdline` handling are copied character by character.
