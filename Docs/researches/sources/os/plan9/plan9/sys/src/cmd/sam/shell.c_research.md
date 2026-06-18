# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/shell.c

Executes external Plan 9 shell commands for `!`, `<`, `>`, and `|` editor commands.

Key functions:
- `plan9` prepares command text, optional pipes, error redirection, fork/exec of `rc`, and data movement between files and commands.
- `checkerrs` reads and reports the downloaded-terminal error file after a shell command.

Behavior notes:
- `|` first snarfs the selected text into `plan9buf`, forks a writer process into a secondary pipe, and runs the command with that pipe as stdin.
- `<` and `|` capture command stdout back into the file through `readio`.
- `>` sends selected file text to the command.
- `!` runs the command with output routed to terminal/error handling.
- In downloaded mode, stderr is redirected to a temporary `sam.err` file for later display.

Risk/maintenance notes:
- Uses nested forks, pipes, and `setjmp(mainloop)` to recover from write-side errors.
- Command text is cached in global `plan9cmd`.
