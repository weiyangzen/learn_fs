# sources/user-network-fs/samba/source3/utils/smbget.c

`smbget.c` implements a wget-like downloader for `smb://` URLs using libsmbclient. It supports recursive traversal, resume, update-if-newer, stdout or named output, progress display, guest and Samba credential handling, SMB encryption, Kerberos options, NT-hash passwords, winbind credential cache use, and rate limiting.

Important pieces are `struct opt`, `get_auth_data_with_context_fn`, `smb_download_dir`, `smb_download_file`, progress formatting helpers, signal handlers, and libsmbclient context setup in `main`. The auth callback synchronizes Samba command-line credentials into libsmbclient. Recursive mode walks directories, workgroups, servers, and file shares while skipping printer/comms/IPC shares.

`smb_download_file` opens and stats the remote file, chooses the local output path, handles update/resume/stdout modes, verifies resume overlap, reads in blocks, optionally rate-limits, writes locally, and updates progress. Persistent state is local files/directories; global counters track summary bytes and elapsed time.

Dependencies include libsmbclient, Samba credentials/gensec/loadparm, POSIX file APIs, terminal sizing, and signals. Risks include local path collisions in recursive mode, mtime-only update decisions, resume behavior needing scrutiny because the remote handle position after overlap verification is subtle, and rate limiting based on `clock()`. Test signals: auth modes, encryption, single/recursive downloads, stdout/output conflicts, resume success/failure, update skips, progress resizing, rate limiting, and clean signal exit.
