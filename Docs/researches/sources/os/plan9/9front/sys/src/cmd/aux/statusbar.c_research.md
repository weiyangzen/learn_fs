# File Research: sources/os/plan9/9front/sys/src/cmd/aux/statusbar.c

`statusbar` displays progress from stdin lines containing `n d`. It can open a new graphical window and draw a green progress bar with percentage text, or fall back to terminal text mode.

Options: `-w` window rectangle, `-t` force text mode, `-k` do not turn Delete/ETX into an interrupt, and optional title. In graphical mode it forks an event watcher so keyboard interrupt can post a note to the parent.

The text mode uses backspaces to update only changed bar content. Graphical mode tracks last pixel width and percent to avoid unnecessary redraws.
