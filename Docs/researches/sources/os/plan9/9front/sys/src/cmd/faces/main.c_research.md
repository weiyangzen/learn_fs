# File Research: sources/os/plan9/9front/sys/src/cmd/faces/main.c

## Purpose
Implements the graphical `faces` mail monitor UI.

## Key Elements
Initializes draw state, fonts, arrow images, plumb ports, and mailbox list; displays sender face tiles with sender name, time/date, and unknown-domain label; handles scrolling, deletion, and opening mail; tracks recent timestamps; supports history mode, initial mailbox load, click-remove mode, and multiple maildirs.

## Dependencies
Uses Plan 9 draw/event/mouse device APIs, plumbing via `initplumb`/`nextface`, face lookup through `findbit`, and multiple rforked processes for main, time updates, and mouse handling.

## Behavior/Risks
Processes share memory with `RFMEM`, so display/list state is protected mainly by `lockdisplay`, not a broader data lock. UI geometry depends on fixed 48-pixel faces and font heights. `killall` posts notes to sibling processes on failure or exit.
