# File Research: sources/windows/dokany/dokan/create.c

Create/open dispatcher for `IRP_MJ_CREATE`, including security-context translation, open-context allocation, create-disposition mapping, target-directory handling, and delete access fallback.

Key responsibilities:
- `SetIOSecurityContext()` converts serialized driver security context fields into user-mode `DOKAN_IO_SECURITY_CONTEXT` pointers and `UNICODE_STRING` views.
- `CreateSuccesStatusCheck()` treats normal success plus selected `STATUS_OBJECT_NAME_COLLISION` cases as successful opens for `FILE_OPEN_IF`, `FILE_SUPERSEDE`, and `FILE_OVERWRITE_IF`.
- `DispatchCreate()` allocates and initializes a `DOKAN_OPEN_INFO`, stores it in `EVENT_INFORMATION.Context`, and calls `DOKAN_OPERATIONS.ZwCreateFile`.
- Splits `CreateOptions` into high-byte disposition and low 24-bit create options.
- Detects directory opens through `FILE_DIRECTORY_FILE` and `SL_OPEN_TARGET_DIRECTORY`.
- Handles `SL_OPEN_TARGET_DIRECTORY` by temporarily opening the original child, then opening its parent directory.
- Maps user callback status into `FILE_OPENED`, `FILE_CREATED`, `FILE_OVERWRITTEN`, `FILE_SUPERSEDED`, `FILE_EXISTS`, or `FILE_DOES_NOT_EXIST`.
- On delete access denial, attempts a parent-directory open with `FILE_DELETE_CHILD` and/or `FILE_LIST_DIRECTORY`.

Important behavior:
- `DOKAN_OPEN_INFO` starts with `OpenCount = 1`; subsequent operations increment/decrement it in `dokan.c`.
- On create failure, the open info is returned to the pool and the result context is cleared.
- On success, `DOKAN_OPEN_INFO` captures `IsDirectory` and user `DOKAN_FILE_INFO.Context`.
- Conflicting `FILE_NON_DIRECTORY_FILE` and `FILE_DIRECTORY_FILE` options return `STATUS_INVALID_PARAMETER`.
- `SL_OPEN_TARGET_DIRECTORY` mutates the request file name in place to parent path form and keeps `origFileName` for child checks.

Dependencies:
- Depends on driver `EVENT_CONTEXT.Operation.Create` layout, including embedded offsets for names and security descriptors.
- Uses pooled open info from `dokan_pool.c`.
- Calls user callbacks `ZwCreateFile`, optionally `Cleanup`, and optionally `CloseFile`.
- Uses Windows create disposition, access mask, and NTSTATUS constants.

Notable risks:
- `SetIOSecurityContext()` trusts driver-provided offsets into the serialized access state.
- `origFileName = _wcsdup(fileName)` is not checked before use in the `SL_OPEN_TARGET_DIRECTORY` child-open path.
- The delete-access fallback mutates `fileName` to the parent path and does not restore it, which is acceptable for reply processing but fragile for later diagnostics.
- A failed `PopFileOpenInfo()` would be dereferenced; allocation failure is not handled locally.
