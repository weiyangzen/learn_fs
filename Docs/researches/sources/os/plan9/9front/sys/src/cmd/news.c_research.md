# File Research: sources/os/plan9/9front/sys/src/cmd/news.c

Displays local Plan 9 news items from `/lib/news`.

Key elements:
- Modes: default prints news newer than `$home/lib/newstime`; `-a` prints all; `-n` prints only names.
- `read_dir` collects news directory entries, injects the previous `newstime` marker, optionally updates it, filters ignored names, and sorts by reverse mtime.
- `eachitem` iterates sorted items until the marker unless printing all.
- `print_item` prints item header with owner and date, then indents nonblank content.
- `note` emits compact `news: item...` output.

Notable behavior:
- Zero-length news files are treated as “in progress” and skipped.
- Ignored names are `core` and `dead.letter`.

Risks and quirks:
- Uses fixed path buffers and `sprint`.
- Does not free allocated news names before exit.
