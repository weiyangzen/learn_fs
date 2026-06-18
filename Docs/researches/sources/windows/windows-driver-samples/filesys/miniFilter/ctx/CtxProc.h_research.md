# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxProc.h

## Purpose
Shared prototype and inline helper header for the `ctx` minifilter sample. It declares callbacks and context helper routines implemented across `operations.c`, `context.c`, and `support.c`, and defines inline resource allocation/acquire/release helpers.

## Key Contents
- Operation callback prototypes:
  - `CtxPreCreate`, `CtxPostCreate`
  - `CtxPreCleanup`
  - `CtxPreClose`
  - `CtxPreSetInfo`, `CtxPostSetInfo`

- Context helper prototypes:
  - File context:
    - `CtxFindOrCreateFileContext`
    - `CtxCreateFileContext`
  - Stream context:
    - `CtxFindOrCreateStreamContext`
    - `CtxCreateStreamContext`
    - `CtxUpdateNameInStreamContext`
  - Stream-handle context:
    - `CtxCreateOrReplaceStreamHandleContext`
    - `CtxCreateStreamHandleContext`
    - `CtxUpdateNameInStreamHandleContext`

- Unicode string support:
  - `CtxAllocateUnicodeString`
  - `CtxFreeUnicodeString`

## Inline Resource Helpers
- `CtxAllocateResource`
  - Allocates an `ERESOURCE` from `NonPagedPool` using `CTX_RESOURCE_TAG`.

- `CtxFreeResource`
  - Frees an `ERESOURCE` allocation using `CTX_RESOURCE_TAG`.

- `CtxAcquireResourceExclusive`
  - Asserts `IRQL <= APC_LEVEL`.
  - Enters a critical region.
  - Acquires the resource exclusively.

- `CtxAcquireResourceShared`
  - Asserts `IRQL <= APC_LEVEL`.
  - Enters a critical region.
  - Acquires the resource shared.

- `CtxReleaseResource`
  - Asserts `IRQL <= APC_LEVEL`.
  - Releases the resource.
  - Leaves the critical region.

## Research Notes
The resource wrappers encode the expected ERESOURCE discipline for the sample: calls must run at or below APC level, and acquisition is paired with critical-region entry so normal kernel APCs cannot interrupt while holding the resource.
