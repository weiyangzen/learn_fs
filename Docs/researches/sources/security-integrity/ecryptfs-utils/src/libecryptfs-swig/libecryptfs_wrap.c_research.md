# sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs_wrap.c

## Purpose
Generated SWIG 1.3.36 Python extension wrapper for a very small libecryptfs API surface. The module is initialized as `init_libecryptfs` and exposes Python-callable bindings for passphrase token blob generation, signature extraction from a blob, and adding a blob to the kernel user keyring.

## Important APIs, types, and functions
- `_wrap_ecryptfs_passphrase_blob(salt, passphrase)` converts Python string-like inputs to `char *`, calls `ecryptfs_passphrase_blob`, and returns the `binary_data` result as a Python string of explicit size.
- `_wrap_ecryptfs_passphrase_sig_from_blob(blob)` returns the password signature embedded in an auth-token blob.
- `_wrap_ecryptfs_add_blob_to_keyring(blob, sig)` forwards a raw blob and expanded-hex signature to libecryptfs and returns an integer status.
- `SWIG_AsCharPtrAndSize`, `SWIG_FromCharPtrAndSize`, and the `PySwigObject`/`PySwigPacked` runtime implement string, pointer, and packed-data conversions.
- `SwigMethods` is the exported Python method table; only the three functions above are bound.

## Control flow
Most of the file is SWIG runtime bootstrap and conversion machinery. Each wrapper parses a Python argument tuple, converts arguments to C buffers, calls the underlying libecryptfs function, converts the return value, releases temporary conversion buffers when SWIG allocated them, and jumps to a shared `fail` path on parse or conversion errors. Module initialization fixes method metadata, creates the Python module, initializes SWIG type information, and installs constants.

## State and persistence behavior
The wrapper itself persists no application state. Its effects are inherited from the called libecryptfs functions: generated auth-token blobs contain key material, and `ecryptfs_add_blob_to_keyring` mutates the caller's Linux user keyring. The returned Python binary strings copy raw C memory into Python objects, but the generated wrapper does not model higher-level ownership or secret zeroization.

## Dependencies and integration points
Depends on the Python 2 C API (`Py_InitModule`, `PyString_*`, `PyCObject_*`) and links against libecryptfs symbols declared near the generated wrapper body. It is normally regenerated from a SWIG interface rather than hand-edited, and it integrates Python callers with `key_management.c`.

## Risks and edge cases
The wrapper is Python 2 era code and will not compile cleanly against modern Python 3 APIs without regeneration or compatibility shims. Binary auth-token blobs may contain NUL bytes, so all call sites must preserve explicit lengths. Sensitive passphrases and token data traverse Python immutable string objects and generated C temporaries without reliable wiping. Error reporting is mostly type-conversion errors plus integer libecryptfs return codes, so Python callers need to interpret negative errno-style values themselves.

## Test signals
Useful tests would import the extension under its target Python version, call `ecryptfs_passphrase_blob` with a known salt/passphrase, extract the signature with `ecryptfs_passphrase_sig_from_blob`, and compare it to libecryptfs C output. Integration tests require a Linux keyring-capable environment to verify `ecryptfs_add_blob_to_keyring`; Python 3 build failure is an expected compatibility signal unless the wrapper is regenerated.
