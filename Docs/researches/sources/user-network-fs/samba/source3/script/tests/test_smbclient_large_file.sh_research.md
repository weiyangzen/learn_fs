# sources/user-network-fs/samba/source3/script/tests/test_smbclient_large_file.sh

## Purpose
This test verifies large POSIX-mode write/read behavior through `smbclient` by uploading and downloading a sparse 20 MiB file on `xcopy_share`.

## Important APIs, Functions, and Control Flow
The script accepts a ccache, `smbclient3`, server, prefix, and extra args. It exports `KRB5CCNAME`, creates `$PREFIX/largefile` using `dd if=/dev/zero seek=$((20 * 1024 * 1024)) count=1 bs=1`, then `test_large_write_read` writes an smbclient command script: `posix`, `put`, `get`, `rm`, `quit`. It expects a successful command and a `getting file` message, then runs `cmp` between the original and downloaded files.

## State, Dependencies, Integration, and Risks
State is temporary files under `$PREFIX` and a server-side `largefile` removed by the smbclient script. It depends on POSIX extensions, xcopy share configuration, disk/sparse-file behavior, and optional Kerberos/additional args. Risks include storage pressure if sparse files become allocated and cleanup gaps if the upload succeeds but later commands fail. The strongest signal is byte-for-byte `cmp`.
