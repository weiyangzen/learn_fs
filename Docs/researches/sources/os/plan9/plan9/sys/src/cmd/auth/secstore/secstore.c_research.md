# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.c

Implements the secstore network client. It logs in with PAK, handles optional STA, and supports get (`-g`), factotum-line get (`-G`), put (`-p`), remove (`-r`), password change (`-c`), server override, user override, stdin password, nvram password, and verbose mode.

File contents are encrypted client-side with AES-CBC using a key derived from the secstore password; the wire is also protected by `SConn`. `getfile` decrypts and authenticates the trailing sentinel, optionally returning file data in memory. `putfile` encrypts local/memory data, sends size, IV, ciphertext, and sentinel.

`chpasswd` sends a new `PAK-Hi`, downloads each file, decrypts with old password, and reuploads encrypted under the new password. The command carefully streams `-G` output line by line for `/mnt/factotum/ctl`.
