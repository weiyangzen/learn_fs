# File Research: sources/os/bsd/netbsd-src/sys/sys/kobj.h

Declares the external kernel object loader interface for ELF modules. It supports loading from VFS or memory, affixing symbols, unloading, querying text address/size, finding sections, symbol lookup, relocation, machine-dependent handling, and namespace rewriting.

It is a key dependency of the module loader. Risks include ELF size selection through `ELFSIZE`, relocation correctness across architectures, object lifetime after unload, and section/symbol table consistency.
