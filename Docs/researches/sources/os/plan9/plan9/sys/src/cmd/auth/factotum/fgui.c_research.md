# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fgui.c

Implements the graphical front end for factotum prompts. It opens `/mnt/factotum/confirm` and `/mnt/factotum/needkey`, starts reader procs for each, parses request attributes, extracts `tag=...`, and serializes handling through a channel in `threadmain`.

The confirmation path builds a control window showing key attributes and `Accept`/`Refuse` controls plus a “remember” checkbox. Remembered answers are stored in an in-memory `Memory` linked list keyed by matching request attributes, then reused without prompting.

The need-key path builds a dynamic form from query attributes, adds two extra blank query rows, fills defaults such as `user=getuser()`, masks private `!` fields with the invisible password font, and writes the completed key to `/mnt/factotum/ctl` as `key %A`.

Important dependencies: Plan 9 draw/control/thread APIs, factotum attr parsing/formatting (`_parseattr`, `%A`), and mounted factotum files. Notable risk: the code comments admit need-key error handling after writing `/mnt/factotum/ctl` is incomplete.
