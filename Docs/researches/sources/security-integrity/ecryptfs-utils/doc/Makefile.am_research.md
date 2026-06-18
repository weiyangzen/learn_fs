# sources/security-integrity/ecryptfs-utils/doc/Makefile.am

Purpose: Automake documentation root.

Important APIs/targets: recurses into `manpage`, installs/distributes FAQ HTML and mount-private text, and conditionally installs PKCS11 helper documentation when `BUILD_PKCS11_HELPER` is enabled.

Control flow/state: `dist_doc_DATA`, `dist_noinst_DATA`, `dist_html_DATA`, and `dist_pkgdata_DATA` decide install/distribution behavior.

Dependencies/integration: controlled by configure conditionals and used by `make dist`.

Risks: PKCS11 doc install changes with build feature flags, which can affect package contents.

Test signals: `make distcheck` and docs install checks.
