# File Research: sources/os/bsd/netbsd-src/lib/csu/common/compident.S

Common assembly source for compiler memory-model ELF notes. It is currently used by SPARC64 builds to create note objects for code models such as `medlow`, `medmid`, and `medany`.

The generated `.note.netbsd.mcmodel` note contains the `NetBSD` name, a note type for memory model tagging, and caller-supplied content/padded length.
