# File Research: sources/os/plan9/plan9/sys/src/cmd/news.c

User-facing Plan 9 `news` command for `/lib/news`. It prints all news (`-a`), names of new items (`-n`), explicit items, or default items newer than the user’s `$home/lib/newstime`, updating that timestamp file on default runs.

`read_dir()` gathers directory entries from `/lib/news`, ignores configured names, optionally records the previous newstime marker, updates the marker file, and sorts entries newest first. `eachitem()` emits entries until it reaches the marker unless printing all.

`print_item()` prints a heading with item name, modifying user, and timestamp, then prints file contents with tab-indented nonblank lines and collapsed leading blank pages. `note()` emits compact names-only output.

Risks are small but legacy: fixed path buffers, no allocation failure handling, and a timestamp marker based on directory file mtime rather than persisted state content.
