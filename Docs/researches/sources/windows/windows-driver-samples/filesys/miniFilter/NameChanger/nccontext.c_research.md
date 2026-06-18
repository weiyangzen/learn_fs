# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nccontext.c

This file manages lifetime for instance contexts and stream handle contexts.

`NcInstanceContextClose` is the `FLT_INSTANCE_CONTEXT` cleanup callback. It asserts the context type and tears down the mapping with `NcTeardownMapping`.

`NcStreamHandleContextClose` is the `FLT_STREAMHANDLE_CONTEXT` cleanup callback. It tears down all per-handle feature state:
- Directory enumeration context via `NcStreamHandleContextEnumClose`.
- Directory notification context via `NcStreamHandleContextNotClose`.
- Find-by-SID context via `NcStreamHandleContextFindBySidClose`.
- Shared `ERESOURCE` lock via `NcFreeEResource`.

`NcStreamHandleContextAllocAndAttach` allocates or retrieves a stream handle context for a file object. It first tries `FltGetStreamHandleContext`; if one exists, it returns that referenced context. Otherwise it allocates a paged-pool stream handle context, zeroes it, allocates the shared lock, initializes notification/enumeration/find-by-SID subcontexts, and attaches it with `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.

Race handling:
- If another thread attaches a context first, `FltSetStreamHandleContext` returns `STATUS_FLT_CONTEXT_ALREADY_DEFINED`; the function converts this to success, returns the existing context, and releases the newly allocated one.
- The function guarantees the returned context has one reference that the caller must release.

Important dependencies:
- Used by directory enumeration, directory notifications, and find-by-SID handling whenever per-handle state is needed.
- Cleanup callbacks depend on each submodule’s close routine being idempotent on zeroed/empty state.
