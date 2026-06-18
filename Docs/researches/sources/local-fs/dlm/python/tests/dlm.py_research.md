# File Research: sources/local-fs/dlm/python/tests/dlm.py

## Purpose
Duplicate copy of the Python ctypes DLM wrapper found at `python/bindings/dlm.py`.

## Contents
- File content matches `sources/local-fs/dlm/python/bindings/dlm.py` byte-for-byte in this checkout.
- Provides the same `LockMode`, `LockFlag`, `LockSBFlag`, `DLMError`, `Lockspace`, and nested `Lock` APIs.

## Notes
- Because this is under `python/tests`, it is likely vendored locally so test scripts can import `dlm` without package installation.

## Risks / Gaps
- Same risks as the binding file: errno loss on create failure, callback lifetime concerns, destructor exceptions, and `c_char` flag handling.
- Duplication means fixes to bindings must be mirrored here unless tests are changed to import the package copy.
