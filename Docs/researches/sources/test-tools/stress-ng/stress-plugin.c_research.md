# sources/test-tools/stress-ng/stress-plugin.c

Purpose: `stress-plugin.c` implements the `plugin` stressor, dynamically loading a user-specified shared object, discovering exported `stress_*` functions, and executing selected plugin methods in isolated child processes.

Important APIs/types/functions: the implementation requires `link.h`, libdl, and non-static builds. `stress_plugin_so()` handles `--plugin-so`: it `dlopen()`s the `.so`, obtains the link map, scans dynamic symbol/string tables for `STT_FUNC` symbols named `stress_*`, builds `stress_plugin_methods`, and stores function pointers from `dlsym()`. `stress_plugin_method_all()` calls every discovered method after index 0. `stress_sig_handler()` counts unexpected signals in shared `sig_count`.

Control flow: option parsing loads and indexes the plugin before support checks. `stress_plugin()` validates the selected method, mmaps shared signal counters, synchronizes, and repeatedly forks. Each child applies scheduler settings, disables dumps, drops capabilities, installs signal handlers, disables stack-smash messages, then calls the selected plugin function until it returns nonzero or the run stops. The parent waits, force-kills on wait errors, and reports counted unexpected signals after shutdown.

State and persistence behavior: global state holds the dlopen handle and discovered method table. Shared anonymous memory holds signal counts. Loaded plugin code remains in process until `dlclose()` at deinit. No files are written by this stressor itself.

Dependencies and integration points: ELF dynamic metadata, libdl `dlopen`/`dlinfo`/`dlsym`, stress-ng option callbacks, capability dropping, fork retry, metrics through bogo counters, and `CLASS_CPU | CLASS_OS` registration with a supported callback requiring a plugin.

Risks: symbol-table parsing assumes ELF layout and uses dynamic table pointers from the loaded object. Plugin code is untrusted and can crash or hang children; isolation is by fork, signal handlers, disabled core dumps, and capability drop. `stress_plugin_methods` is freed at deinit, so option/method lookup order matters.

Test signals: `--plugin-so /path/plugin.so --plugin-method all` should discover methods and bogo-progress. Tests should cover missing/invalid `.so`, no `stress_*` symbols, crashing plugin methods with signal counts, static builds, and method-name enumeration.
