# sources/user-network-fs/s3fs-fuse/src/s3fs_extcred.h

Purpose: defines the C ABI that external credential libraries must implement so s3fs can delegate credential initialization, refresh, version reporting, and cleanup.

Important APIs and types: required symbols are `VersionS3fsCredential(bool detail)` and `UpdateS3fsCredential(...)`. Optional symbols are `InitS3fsCredential(const char*, char**)` and `FreeS3fsCredential(char**)`. Typedefs `fp_VersionS3fsCredential`, `fp_InitS3fsCredential`, `fp_FreeS3fsCredential`, and `fp_UpdateS3fsCredential` match the `dlsym` casts in `s3fs_cred.cpp`. `S3FS_FUNCATTR_WEAK` is intentionally overrideable for internal weak symbol builds.

Control flow: s3fs loads a shared library, resolves the required and optional symbols, calls init once after load, calls update whenever token refresh is needed, and calls free before unload/destruction. Error strings and credential strings are allocated by the plugin and freed by the caller.

State and persistence: this header owns no state. It defines ownership transfer rules for strings and the token expiration value, using `long long` to avoid ABI ambiguity around `time_t`.

Dependencies and integration points: consumed by both s3fs core and external credential-library authors. It must remain C-compatible despite being included from C++.

Risks: ABI drift is high impact: changing argument order, allocation contract, or symbol names breaks plugins. The caller expects heap allocations compatible with `free()`. Plugins run inside the s3fs process, so failures or unsafe code affect the filesystem.

Test signals: build a minimal plugin implementing required-only symbols, a plugin implementing all symbols, and failure plugins that return null strings or invalid expiration. Verify `credlib_opts` propagation and caller-side freeing under sanitizers.
