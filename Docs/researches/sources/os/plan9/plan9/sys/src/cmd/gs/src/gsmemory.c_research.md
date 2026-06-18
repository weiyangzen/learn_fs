# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.c

Generic allocator support for Ghostscript. Defines debug fill-byte constants, structure descriptors for free blocks, byte blocks, GC roots, and const strings, plus bytestring enumeration/relocation helpers that distinguish object-backed bytes from raw string-backed data.

Provides utility functions for debug filling large blocks, resize-or-allocate struct arrays, raw immovable struct allocation, no-op free/consolidation handlers, const-depunting free helpers, bytestring free helpers, structure type accessors, and root registration.

Under `DEBUG`, it traces reference-count operations and attempts to name referenced objects. It also defines `rc_free_struct_only`, and generic GC pointer enumeration/relocation for basic structures using descriptor metadata and optional supertype traversal.
