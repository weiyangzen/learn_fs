# sources/storage-engines/wiredtiger/ext/test/key_provider/CMakeLists.txt

This CMake file builds the WiredTiger test key-provider extension as either a standalone `MODULE` or builtin `OBJECT` target. It defines `HAVE_BUILTIN_EXTENSION_KEY_PROVIDER`, lists `key_provider.h` and `key_provider.c`, selects linkage based on that option, and adds source/generated/config include directories.

The file has no runtime state, but it controls the generated builtin macro that changes symbol export behavior in `key_provider.c`. Its main integration point is avoiding duplicate `wiredtiger_extension_init` symbols in builtin builds while preserving module loading in normal builds. Tests should validate both build modes.
