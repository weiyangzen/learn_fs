
## sources/storage-engines/wiredtiger/ext/encryptors/nop/CMakeLists.txt

Purpose: builds the sample no-op encryptor as a loadable module from `nop_encrypt.c`.

Integration: creates `wiredtiger_nop_encrypt` as a `MODULE`, includes WiredTiger source/generated/config headers, and applies C diagnostic flags. It has no third-party crypto dependency and no builtin-mode configuration.

State: no runtime state here. Risks are sample-extension ABI drift and lack of install logic in this file. Test signals include module load, `add_encryptor("nop")`, and pass-through encrypt/decrypt behavior.
