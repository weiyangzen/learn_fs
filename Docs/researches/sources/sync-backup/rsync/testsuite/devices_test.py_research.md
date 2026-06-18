## sources/sync-backup/rsync/testsuite/devices_test.py

Purpose: executable regression coverage for rsync device handling, including character devices, block devices, FIFOs, hard-linked special files, and the `devices-fake` symlink variant that uses fake-super xattrs instead of real `mknod`.

Important APIs and control flow: imports `rsyncfns` helpers such as `run_rsync`, `checkdiff`, `rsync_ls_lR`, `xattr_set`, `xattrs_supported`, and itemize constants. At startup it detects the script name to select real-device or fake-super mode. Real mode requires root or re-execs through `FAKEROOT_PATH`; fake mode requires xattrs and patches `rsyncfns.RSYNC` and `TLS_ARGS` with `--fake-super`. `make_special()` creates real specials with `os.mkfifo`/`os.mknod` or fake specials via `user.rsync.%stat`. The test probes `rsync -VV` for `hardlink_specials`, builds source nodes, compares focused itemize output for device-number differences, then verifies a full `-aiHvv` transfer and directory listings.

State and dependencies: mutates `FROMDIR`, `TODIR`, optional `CHKDIR`, process environment through helper globals, filesystem device nodes or xattrs, and mtimes. It depends on platform privilege, fakeroot, xattr support, and `tls`.

Integration points: validates receiver/generator itemize semantics, fake-super metadata encoding, hard-link metadata for specials, and `--link-dest` behavior over device entries.

Risks and test signals: skip paths avoid false failures on unsupported systems. Strong signals are exact itemize strings, recursive `tls` listing equality, and hard-linked special output when supported. Main risk is privilege/platform variance around device creation and xattr namespaces.
