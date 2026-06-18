# sources/user-network-fs/samba/source3/script/tests/test_smbclient_mget.sh

## Purpose
This wrapper tests recursive `mget` behavior for a directory and then verifies local cleanup of the fetched files.

## Important APIs, Functions, and Control Flow
Arguments are `smbclient3 server share user password directory`. It changes to `$SELFTEST_TMPDIR`, starts a manual subunit test because `testit` breaks the `-c` command, and invokes `smbclient //$SERVER/$SHARE -U... -c "recurse;prompt;mget $DIRECTORY"`. It emits pass/fail manually, then runs `rm "$DIRECTORY"/foo` and `rmdir "$DIRECTORY"` via `testit`.

## State, Dependencies, Integration, and Risks
It creates downloaded files under `$SELFTEST_TMPDIR/$DIRECTORY` and removes only `foo` plus the directory. It assumes the remote directory contains `foo` and that `mget` creates a matching local directory. Risks include partial downloads leaving residue and limited verification: success is mainly command status and the ability to delete expected local files, not a content comparison.
