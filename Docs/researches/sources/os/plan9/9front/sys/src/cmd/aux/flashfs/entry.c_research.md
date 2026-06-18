# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/entry.c

Role: In-memory object tree and extent index for flashfs.

Data model:
- `Entry` represents files and directories with refcount, name, file number, mode, modification number/time, size, parent, hash/list links, and either directory state or two parity extent lists.
- Directories maintain a small hash table plus a linked list for directory iteration.
- Files keep extents in `gen[2]`, one per journal generation/parity.
- Global `map` maps file numbers to entries; `root`, `used`, `limit`, and `maxwrite` are shared with journal/request code.

Operations:
- `einit` creates root and the file-number map.
- `ecreate`, `eremove`, `ewalk`, `etrunc`, `echmod`, and `edestroy` implement namespace and metadata changes.
- `ewrite` adds a new extent to the active generation; `eread` reconstructs file bytes from active and alternate generation extents, zero-filling holes.
- `esum` moves live extents from one generation to the other during journal summarization.
- `ediropen`, `edirread`, and `edirclose` support stable directory reads and update readers when entries are removed.
- `erenum` rewrites extent sector numbers after sector duplication.

Notable invariants:
- File numbers are regenerated on truncate.
- Directory child modes are masked by parent mode at create time.
- Directory removal is rejected if non-empty.
