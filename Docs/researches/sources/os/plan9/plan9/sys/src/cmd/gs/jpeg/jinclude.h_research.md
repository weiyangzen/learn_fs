# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jinclude.h

Internal JPEG portability include. It includes `jconfig.h`, marks `JCONFIG_INCLUDED`, and centralizes system header selection for the IJG modules.

It pulls in standard headers for `NULL`, `size_t`, `FILE`, allocation, and string/memory functions based on configuration symbols. It defines `MEMZERO` and `MEMCOPY` either through BSD `bzero`/`bcopy` or ANSI `memset`/`memcpy`.

The header also defines `SIZEOF(object)` as a size_t-cast `sizeof`, plus `JFREAD` and `JFWRITE` wrappers around `fread`/`fwrite` with IJG’s preferred argument order and casts.
