# sources/storage-engines/wiredtiger/ext/CMakeLists.txt

Purpose: top-level build integration for WiredTiger loadable extensions.

Important APIs and control flow: adds subdirectories for compressor, collator, encryptor, storage-source, page-log, and test extensions. POSIX-only extensions are gated by `WT_POSIX`, and `ENABLE_PALITE` controls the palite page-log extension. It creates an umbrella `wiredtiger_ext` target, iterates a known list of extension targets, checks whether each target exists and is a `MODULE_LIBRARY`, and adds it as a dependency.

State and persistence: no runtime state; it produces module library build targets and an aggregate build target.

Dependencies and integration: depends on each extension subdirectory declaring expected target names. `wiredtiger_ext` allows runtime consumers that use `dlopen`/extension loading to depend on all available modules without maintaining duplicate lists.

Risks: the target list must stay synchronized with subdirectories and target names. Optional or platform-gated targets are handled gracefully by `if(TARGET ...)`, but a renamed extension would silently drop from the umbrella target.

Test signals: configuring and building `wiredtiger_ext` should build all available module libraries on the current platform.
