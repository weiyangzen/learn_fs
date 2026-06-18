# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9user.c

In-memory user and group database for fossil, plus console commands to read, dump, edit, and write `/active/adm/users`.

Users are stored in a `Ubox` with uid and uname hash tables plus a sorted linked list for stable writeback. The parser strips whitespace/comments, validates four-field `uid:uname:leader:members` records, rejects duplicates and invalid names, enforces mandatory users `adm`, `none`, `noworld`, and `sys`, and fills group memberships on a second pass.

Lookup helpers translate uid/uname and evaluate group membership, group leadership, and the special optional `write` group that can make the filesystem appear read-only to nonmembers. `uname` supports create, rename, leader changes, member add/remove, and automatic home-directory creation; `users` can restore defaults, reread a file, dump counts, and write the current database back through fossil file operations.
