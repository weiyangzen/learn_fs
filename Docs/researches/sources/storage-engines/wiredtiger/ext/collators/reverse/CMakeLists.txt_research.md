# sources/storage-engines/wiredtiger/ext/collators/reverse/CMakeLists.txt

Purpose: builds the reverse string collator as a loadable WiredTiger module.

Important APIs and control flow: sets `sources` to `reverse_collator.c`, creates `wiredtiger_reverse_collator` as a `MODULE` library, adds private include directories for source includes, generated includes, and generated config, and applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`.

State and persistence: no runtime state; produces a module artifact for extension loading.

Dependencies and integration: depends on generated WiredTiger headers in the build tree and strict compiler flags from the broader CMake configuration. The target name is referenced by the top-level `wiredtiger_ext` umbrella.

Risks: include directory ordering must expose generated config before extension compilation. If target name changes, the umbrella dependency list must be updated.

Test signals: module compilation and successful runtime `load_extension`/extension initialization validate integration.
