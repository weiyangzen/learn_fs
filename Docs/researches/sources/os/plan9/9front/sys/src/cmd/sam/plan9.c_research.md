# File Research: sources/os/plan9/9front/sys/src/cmd/sam/plan9.c

`plan9.c` holds Plan 9-specific constants and utility functions for sam.

It defines the synthetic command-file name, click-selection delimiter tables, executable paths (`samterm`, `rx`, shell), environment names, temp directory, and rescue command path.

`dprint`, `print_s`, and `print_ss` route formatted output through `termwrite`. `statfile` and `statfd` extract Plan 9 file identity, mtime, length, and append-only flag from `Dir` data.

`notifyf` handles notes: closed-pipe writes are optionally continued, interrupts continue, and other notes trigger rescue before default handling. `waitfor` waits for a specific child PID and returns its exit status message.

`samerr` constructs the downloaded-mode stderr file path. `emalloc` and `erealloc` are panic-on-failure allocation wrappers that set malloc tags.
