# sources/security-integrity/ecryptfs-utils/src/key_mod/Makefile.am

Purpose: builds installable eCryptfs key module plugins.

Important APIs/targets: always builds passphrase module; conditionally builds OpenSSL, pkcs11-helper, TSPI, and GPG modules. Each libtool module uses `-module -avoid-version -shared` and links relevant provider libraries. Install hook removes `.la` and `.a`; uninstall removes `.so`.

Control flow/state: configure conditionals control plugin set. Modules install under `ecryptfskeymoddir`.

Dependencies/integration: OpenSSL, pkcs11-helper, TrouSerS, GPGME, libgcrypt, and libecryptfs plugin loader contract.

Risks: plugin ABI is the `get_key_mod_ops()` function and operation table; mismatches fail at runtime. Removing static/libtool files is intentional for runtime plugin cleanliness.

Test signals: conditional build/link/install of each enabled plugin and plugin loading by libecryptfs.
