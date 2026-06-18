# sources/user-network-fs/blobfuse2/component/libfuse/extension_handler.h

Purpose: C helper for optional dynamically loaded libfuse extensions. It loads an extension shared library, validates its exported callbacks and signature, initializes it, and exchanges FUSE callback tables between Blobfuse and the extension.

Important APIs/types/functions: global `extHandle`, typedefs `callback_exchanger`, `lib_validator`, and `lib_initializer`, globals `ext_fuse_regsiter_func` and `ext_storage_regsiter_func`, and static functions `load_library`, `unload_library`, `get_extension_callbacks`, and `register_callback_to_extension`. The expected extension symbols are `register_fuse_callbacks`, `register_storage_callbacks`, `validate_signature`, and `init_extension`.

Control flow: `load_library` calls `dlopen(extension_path, RTLD_LAZY)`, resolves the four required symbols with `dlsym`, validates all are present, performs a version-dependent handshake (`__FUSE2__` uses fuse2 call signs, otherwise fuse3 call signs), then calls `init_extension("config.txt")`. Error codes distinguish open failure, missing symbols, invalid signature, and init failure. `get_extension_callbacks` asks the extension to populate the operations table that libfuse will use. `register_callback_to_extension` passes Blobfuse's storage callback table into the extension. `unload_library` closes the handle if present.

State and persistence behavior: state is process-global in static C variables. Loaded library handle and callback function pointers persist until process exit or explicit unload. No files are persisted here, but the extension is always initialized with the literal config filename `config.txt`.

Dependencies/integration points: included by both fuse2 and fuse3 Go cgo handlers. Depends on `dlfcn.h`, libfuse headers, `fuse_operations_t` from `libfuse_defs.h`, and preprocessor build tags to select `fuse.h` vs `fuse3/fuse.h` and handshake strings. Integrated from `Libfuse.initFuse` when `extensionPath` is configured.

Risks: global state is not thread-safe and supports only one extension at a time. `dlerror` details are discarded in favor of numeric codes. On missing symbols or invalid signature, the already-open library is not closed in `load_library` itself. The misspelled `regsiter` names are internal but easy to propagate. Hard-coded `config.txt` limits configurability. Signature strings are simple handshakes, not security boundaries.

Test signals: no direct tests in this subset. Indirect coverage would require `Libfuse.initFuse` with a real extension library; the current libfuse tests do not mount or exercise extension loading.
