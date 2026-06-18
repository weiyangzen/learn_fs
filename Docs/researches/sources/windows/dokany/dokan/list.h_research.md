# File Research: sources/windows/dokany/dokan/list.h

Provides inline Windows-style doubly and singly linked-list helpers.

Key contents:
- Doubly linked-list helpers: `InitializeListHead`, `IsListEmpty`, `RemoveEntryList`, `RemoveHeadList`, `RemoveTailList`, `InsertTailList`, `InsertHeadList`, `AppendTailList`.
- Singly linked-list helpers: `PopEntryList`, `PushEntryList`.
- Uses `LIST_ENTRY` and `SINGLE_LIST_ENTRY` from Windows headers.

Important behavior:
- `IsListEmpty` treats `NULL` as empty.
- `RemoveEntryList(NULL)` returns `TRUE`, assuming an empty-list case.
- No locking is provided; callers must synchronize if lists are shared.

Role in architecture:
- Supplies kernel-style list primitives for user-mode Dokan code without depending on DDK inline definitions.
