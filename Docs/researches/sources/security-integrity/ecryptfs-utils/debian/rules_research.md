# sources/security-integrity/ecryptfs-utils/debian/rules

Purpose: Debian packaging rules using debhelper.

Important APIs/targets: default rule invokes `dh --with autoreconf,python2`; overrides run `autogen.sh`, configure with static build, NSS, PAM, disabled GUI/OpenSSL/PKCS11/TSPI/GPG, optional TPM flags on non-s390, install PAM config, remove useless `.pyc/.la/.a`, gzip debs, set setuid bit on `mount.ecryptfs_private`, strip translation marker from `ecryptfs-record-passphrase`, and create debug package.

Control flow/state: packaging modifies staged `debian/tmp` and `debian/ecryptfs-utils` trees.

Dependencies/integration: Debian build tools, dpkg-buildflags, python2 debhelper addon, pam-auth-update file, and package install manifests.

Risks: `chmod 4755` is a security-sensitive packaging decision. `--fail-missing` makes packaging strict. Python 2 dependency is obsolete in modern distributions.

Test signals: Debian package build, install tree validation, and lintian/security review.
