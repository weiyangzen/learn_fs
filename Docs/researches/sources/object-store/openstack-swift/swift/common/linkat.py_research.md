# sources/object-store/openstack-swift/swift/common/linkat.py

Purpose: exposes Linux `linkat(2)` hard-link functionality to Swift code through a small ctypes wrapper.

Important APIs/types/functions: the internal `Linkat` class defines `AT_FDCWD`, `AT_SYMLINK_FOLLOW`, `available`, and `__call__`; the module exports a singleton `linkat` and deletes the class name from the module namespace.

Control flow: construction loads libc via `find_library('c')`, looks up `linkat`, configures ctypes argument and return types, and attaches an error checker that raises `IOError` with errno text when libc returns -1. Calling validates directory fds are integers, encodes string paths as UTF-8, checks availability, and invokes libc.

State and persistence: stores the resolved libc function pointer. The syscall creates a durable hard link when successful; the wrapper itself has no persistent state.

Dependencies and integration: depends on `ctypes`, `ctypes.util.find_library`, and `os.strerror`. Used where Swift needs atomic/relative hard-link operations not provided portably by Python.

Risks: only available on platforms with libc `linkat`; path encoding is fixed to UTF-8; errno capture depends on ctypes `use_errno`; callers must understand hard-link semantics, permissions, and cross-filesystem limitations. Tests should cover unavailable fallback, fd type validation, string/bytes paths, successful links, and errno propagation.
