# File Research: sources/virtualization/guestfs-tools/lib/guestfs-internal-all.h

## Role

Shared internal header for definitions used across all libguestfs C code, including daemon, library, bindings, and virt tools.

## Contents

The header defines GCC compatibility helpers, `ATTRIBUTE_UNUSED`, string comparison macros such as `STREQ`, `STRPREFIX`, and `STRSUFFIX`, `MAX`/`MIN`, `SOCK_CLOEXEC` fallback, and Apple XDR naming compatibility.

It provides `ADD_ARG`, a bounded helper macro for building short argv arrays with abort-on-overflow behavior.

It defines `is_zero`, an inline zero-buffer test that checks up to the first 16 bytes and then compares the rest of the buffer to the first 16-byte window.

It also defines `COMPILE_REGEXP`, a constructor/destructor macro for compiling PCRE2 regexes at load time and freeing them at unload time.

Finally it declares `mountable_type_t` with device, btrfs subvolume, and already-mounted path variants.

## Research Notes

This file centralizes low-level portability and utility macros that many tools rely on indirectly.
