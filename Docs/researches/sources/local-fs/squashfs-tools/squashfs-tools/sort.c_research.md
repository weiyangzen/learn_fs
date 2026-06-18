# File Research: sources/local-fs/squashfs-tools/squashfs-tools/sort.c

Implements sort-file parsing and priority-ordered file write scheduling. Sort priorities range from -32768 to 32767 and are stored offset by 32768 in `priority_list[65536]`.

`read_sort_file()` handles comments, blank lines, escaped characters in filenames, line-length limits, strict priority parsing, trailing-junk rejection, and stat resolution. Relative entries are resolved against source directories unless mkisofs-style behavior is detected, in which case it warns and treats entries relative to current working directory.

`generate_file_priorities()` walks the directory tree, inheriting directory priority and adding regular files to priority buckets. `sort_files_and_write()` walks highest to lowest priority, writes unread files via `write_file()`, and logs duplicate or hardlink status.

The inode/device hash in `sort_info_list` lets priorities attach to files by stat identity, not just path string.
