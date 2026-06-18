# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmspace.h

Defines interpreter VM-space tags and store-check rules. VM space is encoded in ref attribute bits as `avm_foreign`, `avm_system`, `avm_global`, or `avm_local`, with helper macros to get, index, and set ref space.

The file documents Ghostscript’s extension of PostScript local/global VM rules into four generations. Stores are legal only when the referenced object is not from a younger space than the destination. Macros include `r_is_local`, `r_is_foreign`, `store_check_space`, `store_check_dest`, and compatibility `check_store_space`.

It also documents special systemdict-related exceptions handled elsewhere for initialization and global operators.
