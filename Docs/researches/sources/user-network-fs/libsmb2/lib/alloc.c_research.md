# sources/user-network-fs/libsmb2/lib/alloc.c

Purpose: Implements libsmb2's simple hierarchical allocation context, letting decoded compound objects own child allocations and be freed with one call.

Important APIs/functions: `smb2_alloc_init` allocates a zeroed root block with a hidden `smb2_alloc_header`. `smb2_alloc_data` allocates a zeroed child block with hidden `smb2_alloc_entry`, links it into the root header, and returns the child payload. `smb2_free_data` frees all linked children then the root. `container_of` is used to recover hidden headers, with an MSVC fallback.

Control flow: The caller receives only `buf` pointers. Child allocations prepend each new entry to `hdr->mem`. Free walks the singly linked list and frees entries before freeing the header.

State/persistence: Allocation ownership persists through the hidden root header. There is no global state and no locking; contexts are caller-thread-owned.

Dependencies/integration: Used throughout decode paths, including DCE/RPC payload trees and SMB2 query-info data structures. Errors are reported with `smb2_set_error` when child allocation fails.

Risks: `memctx` passed to `smb2_alloc_data` must be a root pointer from `smb2_alloc_init`; passing child pointers or external memory corrupts ownership assumptions. Individual child frees are unsupported. Size arithmetic adds header offsets without overflow checks. The unused `smb2` parameter in `smb2_alloc_init` is only for API symmetry.

Test signals: Unit tests should allocate root/children, verify zero initialization and tree freeing, exercise allocation failure paths, and run with ASan/UBSan. Decode tests that call `dcerpc_free_data` or `smb2_free_data` are good integration coverage.
