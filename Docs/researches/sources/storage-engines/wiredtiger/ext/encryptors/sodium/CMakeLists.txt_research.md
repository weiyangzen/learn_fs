
## sources/storage-engines/wiredtiger/ext/encryptors/sodium/CMakeLists.txt

Purpose: defines the libsodium encryptor build.

Integration: `HAVE_BUILTIN_EXTENSION_SODIUM` depends on `HAVE_LIBSODIUM`, conflicts with `ENABLE_SODIUM`, and builds `wiredtiger_sodium` as builtin `OBJECT` or loadable `MODULE`. The target includes WiredTiger headers, links `wt::sodium`, applies diagnostics, sets PIC, and installs dynamic builds.

State: none here. Risks include a minor diagnostic typo in the fatal-error string and dependency availability. Test signals include dependency-missing configuration, builtin/dynamic builds, installation, and runtime key handling in `sodium_encrypt.c`.
