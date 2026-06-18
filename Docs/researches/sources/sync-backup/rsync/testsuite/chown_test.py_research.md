# sources/sync-backup/rsync/testsuite/chown_test.py

Purpose: verifies ownership preservation in real `--super` mode and, when invoked as the fake symlink variant, `--fake-super` ownership emulation via xattrs.

Important APIs/types/functions: script-name `fake_variant` detection, `xattrs_supported`, `xattr_set`, `RSYNC_PREFIX`, mutation of `rsyncfns.RSYNC` and `TLS_ARGS`, `chown_or_fake`, optional fakeroot re-exec, and `checkit`.

Control flow: select fake or real behavior. Fake mode encodes uid/gid in rsync fake-super `%stat` xattrs and adds `--fake-super`; real mode adds `--super` and may re-exec under `FAKEROOT_PATH`. Create two files, set distinct uid/gid pairs, then sync and compare.

State and persistence behavior: source ownership is either real inode uid/gid or fake-super xattr state. Destination listing must reflect the same ownership semantics.

Dependencies and integration points: root/fakeroot for real chown, xattr support for fake mode, rsync fake-super metadata, and harness listing.

Risks and test signals: skips if chown or xattrs are unavailable. Failures mean ownership metadata is not preserved or fake-super encoding is mishandled.
