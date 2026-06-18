# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/exec.c

Command execution and text-action dispatcher for Abaco.

Key responsibilities:
- Maps tag commands such as `New`, `Del`, `Get`, `Go`, `Back`, `Forward`, `Paste`, `Snarf`, `Stop`, `Sort`, `Debug`, and `Newcol` to handlers.
- Parses executable command text from tags or selections.
- Implements browser navigation commands and page lookup/open behavior.
- Handles snarf/cut/paste over text widgets.
- Expands selections around URL-like or word-like text.
- Implements search across text buffers.
- Handles plumber look events by opening URLs or matching pages.

Dependencies:
- Uses `Text`, `Window`, `Page`, `Runestr`, Plan 9 plumbing messages, and page/window functions.
- Depends on `pageget`, `pageload`, `winaddhist`, `wingohist`, `rowadd`, `coladd`, `putsnarf`, and `getsnarf`.

Notable risks:
- Command parsing is intentionally Acme-like and selection-sensitive.
- URL expansion/open behavior depends on `validurl` and `urlcombine`.
