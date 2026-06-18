<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dlopen.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_dlopen.c

## Purpose
Provides Windows dynamic-symbol lookup support for the extension API, currently supporting symbols in the current binary.

## Important APIs, Types, and Functions
`__wt_dlopen`, `__wt_dlsym`, and `__wt_dlclose` operate on `WT_DLH`.

## Control Flow
`__wt_dlopen` allocates a handle structure, stores a display name, and for `path == NULL` uses `GetModuleHandleExW`; non-NULL DLL loading is marked TODO and breaks into the debugger. `__wt_dlsym` calls `GetProcAddress`, optionally errors if missing. `__wt_dlclose` calls `FreeLibrary` and frees memory.

## State and Persistence Behavior
Only process module handles and memory are affected. No persistent state.

## Dependencies and Integration Points
Used by extension loading and symbol lookup on Windows. Integrates with Windows error formatting/mapping.

## Risks and Edge Cases
Non-NULL path support is incomplete. The implementation duplicates `dlh->name` twice, leaking the first allocation unless hidden by allocator behavior. Closing a handle obtained from the current process module needs careful Windows reference-count semantics.

## Test Signals
Tests should cover local symbol lookup, missing optional/required symbols, non-NULL path behavior, and leak detection around open/close.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_dlopen.c -->
