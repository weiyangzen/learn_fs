## sources/security-integrity/attr/include/attributes.h

Purpose: deprecated IRIX-compatible extended-attributes API.

It defines namespace and operation flags, maximum value length, list result structures (`attrlist_t`, `attrlist_ent_t`, cursor), multi-operation structures, opcodes, and exported functions `attr_get`, `attr_set`, `attr_remove`, `attr_list`, `attr_multi` and fd variants. Control/integration is implemented in `libattr.c` by mapping IRIX names to Linux xattr namespaces. State is caller-owned buffers and cursors. Dependencies are `stdint.h`, errno values, and install-time replacement of `EXPORT`. Risks include deprecated API use, fixed ABI structures, cursor semantics over mutable xattr lists, and `ATTR_ROOT` privilege requirements. Tests should cover namespace mapping, list packing, multi-op error reporting, and fd/path variants.
