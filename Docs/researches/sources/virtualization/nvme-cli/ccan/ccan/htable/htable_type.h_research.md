# File Research: sources/virtualization/nvme-cli/ccan/ccan/htable/htable_type.h

- Purpose: macro generator for type-safe hash table wrappers.
- Key macro: `HTABLE_DEFINE_TYPE(type, keyof, hashfn, eqfn, name)`.
- Generated API: typed init, sized init, count, clear, copy, add, delete, delete by key, get, getfirst/getnext, delval, pick, first/next/prev.
- Type handling: `HTABLE_KTYPE` uses `typeof(keyof((const type *)NULL))` when available.
