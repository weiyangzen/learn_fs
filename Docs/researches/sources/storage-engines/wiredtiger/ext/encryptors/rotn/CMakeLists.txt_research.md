
## sources/storage-engines/wiredtiger/ext/encryptors/rotn/CMakeLists.txt

Purpose: builds the ROT-N/Vigenere demonstration encryptor.

Integration: creates `wiredtiger_rotn` as a loadable `MODULE`, includes WiredTiger headers, and applies C diagnostic flags. It has no external crypto dependency and no builtin build mode.

State: no runtime state in CMake. Risks are example-only crypto being accidentally mistaken for secure encryption. Test signals include module loading and configuration paths handled by `rotn_encrypt.c`, especially `rotn_force_error`.
