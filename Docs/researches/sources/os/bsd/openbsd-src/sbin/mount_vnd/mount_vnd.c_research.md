# File Research: sources/os/bsd/openbsd-src/sbin/mount_vnd/mount_vnd.c

`mount_vnd.c` configures a vnode disk device for an image file via `VNDIOCSET`. It accepts optional encryption keys, PKCS#5-derived keys, mount options placeholder `-o`, salt file, and disk geometry type.

`get_pkcs_key()` reads a passphrase from a TTY, obtains or creates a 128-byte salt file, derives a Blowfish-sized key with `pkcs5_pbkdf2()`, and zeroes the passphrase. Plain `-k` uses `getpass()` and raw passphrase bytes. The program warns that softraid crypto should be considered instead.

`config()` opens the vnd device with `opendev()`, fills `struct vnd_ioctl` with image path, sector geometry, and optional key material, issues `VNDIOCSET`, closes the device, and explicitly zeroes key memory before returning.

Security-relevant details: salt files are created mode `0600`, passphrases are zeroed for the PKCS path, derived/raw key buffers are zeroed after ioctl, and `-k`/`-K` are mutually exclusive.
