## sources/sync-backup/rsync/testsuite/hardlinks_test.py

Purpose: comprehensive hard-link regression test for `-H`, incremental recursion, remote-shell transfers, alternate basis dirs, checksum mode, and single-file/single-directory edge cases.

Important APIs and control flow: creates three linked names and one copied file, plus a large `text` file from source `.c` files. It checks local `-aHivv`, delta overwrite preservation, then adds many small files and a deep hard link to stress incremental recursion over `lsh.sh`. It tests `--link-dest`, `--copy-dest`, and a `--checksum` run that must not copy an outside-linked `solo`. Finally it verifies single-file and single-directory `-H` copies through `diff`.

State and dependencies: uses hard links, many generated files, `CHKDIR`, `TODIR`, `OUTFILE`, `RSYNC_PEER`, and remote shell support.

Integration points: validates hard-link tables across sender/receiver modes, basis dirs, checksum, and protocol edge cases.

Risks and test signals: exact tree comparisons and output absence of `solo` are key. It skips only if initial hard-link creation is unsupported.
