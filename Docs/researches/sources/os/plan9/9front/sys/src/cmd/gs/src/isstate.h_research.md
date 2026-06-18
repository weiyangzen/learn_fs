# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isstate.h

Defines `struct alloc_save_s`, the saved allocator state object used by `isave.c`. Its first field is a complete `gs_ref_memory_t state`, allowing it to act as a saved allocator snapshot. Additional fields record VM spaces, whether names must be restored, whether the saved allocator was current, the save ID, and opaque client data.

Provides `private_st_alloc_save`, the GC descriptor macro for save objects, built as a suffix of `st_ref_memory` with `client_data` as an extra pointer.
