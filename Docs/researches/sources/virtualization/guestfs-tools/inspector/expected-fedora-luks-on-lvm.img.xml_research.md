# File Research: sources/virtualization/guestfs-tools/inspector/expected-fedora-luks-on-lvm.img.xml

## Purpose

This is the expected XML output for `virt-inspector` when inspecting the phony Fedora guest image `fedora-luks-on-lvm.img`. The test case covers the topology "LUKS on LVM": an LVM volume group is created on `/dev/sda2`, then multiple logical volumes are individually formatted as LUKS devices. The root filesystem is inside the opened LUKS mapping for the `Root` logical volume.

The corresponding test is `sources/virtualization/guestfs-tools/inspector/test-virt-inspector-luks-on-lvm.sh`. It invokes `virt-inspector` with explicit `--key` arguments for `/dev/Volume-Group/Root` and sibling logical volumes, validates the output against `virt-inspector.rng`, then diffs it against this fixture after replacing the `ROOTUUID` placeholder with the runtime LUKS UUID.

## File Shape

- XML document with root `<operatingsystems>`.
- Contains exactly one `<operatingsystem>`.
- Size: 2,261 lines, 105,562 bytes.
- SHA-256: `e1c2b8a818a23b50914bb82ac3f280a4f6b22f7c739ea9c1187a25448aab19ef`.
- Parsed successfully as XML.
- Tag counts include 172 `<application>` records, 2 `<filesystem>` records, and 2 `<mountpoint>` records.

## Inspected OS Identity

The fixture identifies a Linux Fedora guest:

- `<root>`: `/dev/mapper/luks-ROOTUUID`
- `<name>`: `linux`
- `<arch>`: `x86_64`
- `<distro>`: `fedora`
- `<product_name>`: `Fedora release 14 (Phony)`
- `<major_version>` / `<minor_version>`: `14` / `0`
- `<package_format>`: `rpm`
- `<package_management>`: `yum`
- `<hostname>`: `fedora.invalid`
- `<osinfo>`: `fedora14`

The `ROOTUUID` token is intentionally not a literal UUID in the fixture. The test script obtains the actual LUKS UUID with `guestfish luks-uuid /dev/Volume-Group/Root` and substitutes it before diffing.

## Mountpoints And Filesystems

The expected mount map is:

- `/` from `/dev/mapper/luks-ROOTUUID`
- `/boot` from `/dev/sda1`

The expected filesystem inventory is:

- `/dev/mapper/luks-ROOTUUID`: `ext2`, label `ROOT`, UUID `01234567-0123-0123-0123-012345678902`
- `/dev/sda1`: `ext2`, label `BOOT`, UUID `01234567-0123-0123-0123-012345678901`

This validates that `virt-inspector` reports the decrypted mapper node as the root device for LUKS-on-LVM, while still finding the unencrypted boot partition.

## Application Inventory

The `<applications>` section contains 172 RPM application records. Each record has `name`, `version`, `release`, `arch`, `url`, `summary`, and `description`; 11 records also include `epoch`. Architecture distribution is 143 `x86_64`, 27 `noarch`, and 2 `(none)` records. The `(none)` records are both `gpg-pubkey` entries.

The package rows are identical to `expected-fedora-lvm-on-luks.img.xml`; only the root/mountpoint/filesystem device names differ between the two fixtures.

Package names, in fixture order:
`alternatives`, `audit-libs`, `authselect`, `authselect-libs`, `basesystem`, `bash`, `bzip2-libs`, `ca-certificates`, `coreutils`, `coreutils-common`, `cpio`, `cracklib`, `crypto-policies`, `crypto-policies-scripts`, `cryptsetup-libs`, `curl`, `cyrus-sasl-lib`, `dbus`, `dbus-broker`, `dbus-common`, `device-mapper`, `device-mapper-libs`, `diffutils`, `dracut`, `elfutils-debuginfod-client`, `elfutils-default-yama-scope`, `elfutils-libelf`, `elfutils-libs`, `expat`, `fedora-gpg-keys`, `fedora-release`, `fedora-release-common`, `fedora-release-identity-basic`, `fedora-repos`, `fedora-repos-rawhide`, `file`, `file-libs`, `filesystem`, `findutils`, `fuse-libs`, `gawk`, `gawk-all-langpacks`, `gdbm-libs`, `gettext`, `gettext-libs`, `glibc`, `glibc-common`, `glibc-gconv-extra`, `glibc-minimal-langpack`, `gmp`, `gpg-pubkey`, `gpg-pubkey`, `grep`, `grub2-common`, `grub2-tools`, `grub2-tools-minimal`, `grubby`, `gzip`, `json-c`, `kbd`, `kbd-misc`, `kernel`, `kernel-core`, `kernel-modules`, `keyutils-libs`, `kmod`, `kmod-libs`, `kpartx`, `krb5-libs`, `libacl`, `libarchive`, `libargon2`, `libattr`, `libblkid`, `libbpf`, `libbrotli`, `libcap`, `libcap-ng`, `libcbor`, `libcom_err`, `libcurl`, `libdb`, `libeconf`, `libevent`, `libfdisk`, `libffi`, `libfido2`, `libgcc`, `libgcrypt`, `libgomp`, `libgpg-error`, `libidn2`, `libkcapi`, `libkcapi-hmaccalc`, `libmount`, `libnghttp2`, `libnsl2`, `libpsl`, `libpwquality`, `libseccomp`, `libselinux`, `libsemanage`, `libsepol`, `libsigsegv`, `libsmartcols`, `libssh`, `libssh-config`, `libstdc++`, `libtasn1`, `libtirpc`, `libunistring`, `libutempter`, `libuuid`, `libverto`, `libxcrypt`, `libxcrypt-compat`, `libxkbcommon`, `libxml2`, `libzstd`, `linux-firmware`, `linux-firmware-whence`, `lua-libs`, `lz4-libs`, `memstrack`, `mkpasswd`, `mpdecimal`, `mpfr`, `ncurses-base`, `ncurses-libs`, `openldap`, `openssl-libs`, `openssl-pkcs11`, `os-prober`, `p11-kit`, `p11-kit-trust`, `pam`, `pam-libs`, `pcre`, `pcre2`, `pcre2-syntax`, `pigz`, `popt`, `procps-ng`, `publicsuffix-list-dafsa`, `python-pip-wheel`, `python-setuptools-wheel`, `python-unversioned-command`, `python3`, `python3-libs`, `qrencode-libs`, `readline`, `rpm`, `rpm-libs`, `sed`, `setup`, `shadow-utils`, `sqlite-libs`, `systemd`, `systemd-libs`, `systemd-networkd`, `systemd-pam`, `systemd-resolved`, `systemd-udev`, `tpm2-tss`, `tzdata`, `util-linux`, `util-linux-core`, `whois-nls`, `xkeyboard-config`, `xz`, `xz-libs`, `zlib`.

Epoch-bearing package records are `dbus`, `dbus-common`, `findutils`, `gdbm-libs`, `gmp`, `grub2-common`, `grub2-tools`, `grub2-tools-minimal`, `libbpf`, `openssl-libs`, and `shadow-utils`.

## Related Generation Logic

The image is generated by `sources/virtualization/guestfs-tools/test-data/phony-guests/make-fedora-img.pl` under `LAYOUT=luks-on-lvm`. That builder creates VG `Volume-Group` on `/dev/sda2`, logical volumes `Root`, `Logical-Volume-1`, `Logical-Volume-2`, and `Logical-Volume-3`, formats each LV as LUKS with separate passwords, opens them as mapper devices, and creates the phony root filesystem on `/dev/mapper/Root-luks`.

## Maintenance Notes

This fixture is intentionally sensitive to stable XML ordering and exact text emitted by `virt-inspector`. Changes to package inspection, RPM metadata formatting, device naming, LUKS mapper naming, filesystem label/UUID reporting, or osinfo detection can require updating this expected output. For this specific fixture, preserve the `ROOTUUID` placeholder unless the test script is changed, because the runtime LUKS UUID is substituted before diffing.
