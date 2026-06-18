# File Research: sources/os/plan9/9front/sys/src/cmd/sam/multi.c

`multi.c` manages sam's global list of open files and the terminal file menu metadata.

`newfile` creates a `File`, inserts it into the menu list, assigns a protocol tag, and emits `Hnewname` when downloaded. `delfile` removes a file, emits `Hdelname`, and closes file resources.

`fullname`, `fixname`, and `sortname` normalize paths relative to `curwd`, clean names, shorten names by stripping the current directory prefix, maintain sorted menu order, and warn on duplicate names.

`state` transitions a file between clean and dirty display states, sends `Hclean`/`Hdirty` as needed, clears unread state, and avoids marking the command file.

`lookfile` searches the open file list by exact `String` filename.
