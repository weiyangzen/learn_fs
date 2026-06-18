# sources/user-network-fs/samba/source3/script/tests/test_zero_data.sh

Purpose: verifies SMB2 `ZERO_DATA` sparse-file behavior through smbtorture and local disk allocation checks.

Important functions and APIs: uses `dd`, `du -k`, `smbtorture smb2.set-sparse-ioctl`, `smbtorture smb2.zero-data-ioctl`, and subunit. It passes torture options for filename, offset, and `beyond_final_zero`.

Control flow: create `$LOCAL_PATH/zero_data/testfile` with 128 KiB of random data, assert allocated size is 128 KiB, set the file sparse through SMB2 IOCTL, zero the full range through SMB2 `zero-data-ioctl`, then assert local allocation drops to zero KiB.

State and persistence: creates and removes `$LOCAL_PATH/zero_data`. It writes a real file on the backing filesystem and relies on sparse allocation reporting.

Dependencies and integration: registered as `samba3.blackbox.zero-data` in the `fileserver` loop. Requires a filesystem that reports sparse allocation as expected and supports Samba's zero-data path.

Risks and test signals: `chmod 777 p $TESTDIR` appears malformed and may emit an error, though the script continues. Allocation sizes are filesystem-dependent; non-sparse or block-accounting differences can cause false failures. Passing signal is allocation dropping from 128 to 0 after the SMB2 zero operation.
