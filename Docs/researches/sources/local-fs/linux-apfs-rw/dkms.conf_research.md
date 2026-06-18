# File Research: sources/local-fs/linux-apfs-rw/dkms.conf

This is the DKMS packaging configuration for the module.

Fields:
- `PACKAGE_NAME="linux-apfs-rw"`.
- `PACKAGE_VERSION="0.3.20"`.
- Builds module name `apfs`.
- Installs to `/extra`.
- Enables `AUTOINSTALL="yes"`.
- Runs `PRE_BUILD="genver.sh"`.

Research relevance: DKMS uses this file to build and install the out-of-tree `apfs` kernel module automatically. `genver.sh` also uses `PACKAGE_VERSION` as a fallback version source when git metadata is unavailable.
