# sources/user-network-fs/samba/source3/script/tests/test_smbclient_tarmode.sh

## Purpose
This shell test performs an end-to-end smoke test of `smbclient` tarmode creation and extraction using local random file corpora and server-side tar operations.

## Important APIs, Functions, and Control Flow
It accepts server, IP, credentials, local path, prefix, and `SMBCLIENT`, then wraps with `$VALGRIND`. Helpers include `have_command`, `create_test_data`, `validate_data`, `test_tarmode_creation`, and `test_tarmode_extraction`. Creation mode builds local data, runs `smbclient ... -c "tarmode full" -Tc "$PREFIX/tarmode.tar" "/smbclient_tar"`, extracts the tar locally, and diffs extracted content against the local corpus. Extraction mode builds a tar locally and uses `smbclient ... -Tx "$PREFIX/tarmode.tar"` to restore it to the share, then diffs share-backed data.

## State, Dependencies, Integration, and Risks
State spans `$LOCAL_PATH`, `$PREFIX/tarmode`, `$PREFIX/tarmode.tar`, and remote `smbclient_tar` under the `tarmode` share. It depends on `tar`, `dd`, optional `od`, `/dev/urandom`, and the server share. Cleanup is repeated but not trap-based, so interruption can leave tar data. Test signals are command success plus recursive `diff -r`.
