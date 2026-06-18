# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/mdir.c

This file implements the directory-of-message-files backend for `upas/fs`.

Key behavior:
- Recognizes message files named as timestamp sequence IDs (`<seconds>.<seq>`).
- `mdirread` stats and reads directory entries, sorts by parsed fileid, merges new/deleted messages into mailbox state, and skips bad sizes/directories.
- `mdirfetch` reads byte ranges from the corresponding message file.
- `mdirdelete` removes the message file and marks it out of mailbox.
- `idxr/idxw` store directory qid/time metadata in index headers and accept fresh matching index state.
- `mdirmbox` initializes backend callbacks for directory mailboxes and can create directories with `DMcreate`.

Integration and risks:
- `dirskip` is exported and reused by removal code.
- Index freshness is accepted for up to four hours if qid metadata matches/newer.
