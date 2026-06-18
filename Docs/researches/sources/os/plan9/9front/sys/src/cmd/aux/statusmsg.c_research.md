# File Research: sources/os/plan9/9front/sys/src/cmd/aux/statusmsg.c

`statusmsg` displays the latest line read from stdin, either in a new graphical window or in terminal text mode. It shares window-opening and keyboard-interrupt behavior with `statusbar`.

Options are `-w`, `-t`, `-k`, and optional title. Graphical mode clears and redraws the message area each update; text mode overwrites prior text with backspaces and can prefix the title.

It uses `Bsize` allocation for the message buffer and `utfnlen` to avoid splitting the line incorrectly when copying.
