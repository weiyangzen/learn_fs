# sources/security-integrity/ecryptfs-utils/configure.ac

Purpose: Autoconf configuration script for ecryptfs-utils version 104.

Important APIs/macros: initializes package/config headers, libtool, compiler, gettext/intltool, Python/SWIG, and many feature switches: NSS, pywrap, OpenSSL, pkcs11-helper, TSPI, GPG, PAM, GUI, docs/docs-gen, tests, and mudflap. Defines `ECRYPTFS_DEFAULT_KEY_MOD_DIR`, substitutes library flags and install directories, and emits Makefiles for doc, src, key modules, daemon, desktop, PAM, SWIG, tests, and po.

Control flow: options default mostly to detect/no/yes depending on feature. Dependency checks fail explicitly when a requested feature is missing. Docs generation requires TeX/postscript tools. Kernel version support is not checked here, but `/dev/ecryptfs` support is a daemon runtime check.

State/persistence: writes generated `config.h`, Makefiles, pkg-config file, and configured desktop files.

Dependencies/integration: keyutils is mandatory; NSS can become crypto backend; OpenSSL, pkcs11-helper, TrouSerS, GPGME, PAM, GTK, Python, SWIG, gettext, and intltool are optional/conditional.

Risks: old shell tests use `==`, which is not portable to all `/bin/sh` implementations. Python wrapper targets are Python 2-era. Feature defaults influence security surface, especially key modules and PAM.

Test signals: configure-time dependency failures, conditional build coverage, and generated Makefiles.
