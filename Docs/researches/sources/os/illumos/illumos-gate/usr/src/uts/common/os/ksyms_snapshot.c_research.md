# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ksyms_snapshot.c

## Purpose

`ksyms_snapshot.c` builds an ELF-format snapshot of the kernel symbol table for the ksyms subsystem. It walks loaded symbol sections, rewrites symbol/string offsets into a compact snapshot, emits ELF/program/section headers, and returns the size required or emitted.

Read completely: 207 lines.

## Main Responsibilities

- Defines a small synthetic ELF container containing program headers, `.symtab`, `.strtab`, and `.shstrtab`.
- Walks all allocated symbol-table sections in `ksyms_arena`.
- Emits local symbols, global symbols, and strings as separable passes.
- Rewrites each emitted symbol's `st_name` to the snapshot string-table offset and forces `st_shndx` to `SHN_ABS`.
- Computes total snapshot size even when the caller buffer is too small.
- Protects symbol snapshot consistency with `ksyms_lock` as a reader.

## Important Data Structures And Globals

- `ksyms_header_t`: synthetic ELF header, two program headers, four section headers, and section-name string table.
- `ksyms_walkinfo_t`: walk state containing emit callback, target pointer, remaining buffer length, total logical size, selected action mask, and per-action byte totals.
- `ksyms_shstrtab`: fixed section-name string table for `.symtab`, `.strtab`, and `.shstrtab`.
- Action flags: `KW_HEADER`, `KW_LOCALS`, `KW_GLOBALS`, and `KW_STRINGS`.
- `ksyms_lock`: global readers-writer lock for symbol snapshot operations.
- `ksyms_arena`: vmem arena whose allocations are walked to find symbol sections.

## Walk And Emit Flow

`ksyms_emit()` accounts bytes for an action and copies them only if that action is selected and enough buffer space remains after subtracting the requested size. It always advances total logical size for selected actions, letting callers learn the required snapshot length.

`ksyms_walk_one()` interprets each walked allocation as a symbol section header, finds the linked string table, iterates symbols from index 1, copies each symbol to a temporary, rewrites the symbol name offset to the current snapshot string-table size, marks it absolute, and emits the symbol as local or global according to `ELF_ST_BIND()`. It then emits the corresponding NUL-terminated name string.

`ksyms_walk()` initializes walk state, optionally emits the synthetic header, emits the required zero symbol and initial empty string, walks `ksyms_arena`, and returns total selected size.

## Snapshot Construction

`ksyms_snapshot()` first performs a sizing walk over all actions. It then constructs `ksyms_header_t` by copying the running kernel module ELF header and overriding offsets/counts for this synthetic image. It creates two load program headers from `s_text`/`e_text` and `s_data`/`e_data`, with the data segment marked read/write/execute.

The `.symtab` section starts immediately after the synthetic header and contains locals followed by globals. Its `sh_info` is the count of local symbols. The `.strtab` section follows the symbol table. The `.shstrtab` section points into the embedded `shstrings` member. Finally, it emits header, locals, globals, and strings as four ordered walks under the read lock.

## Notable Risks And Invariants

- The code assumes `ksyms_arena` allocations walked with `VMEM_ALLOC` are symbol-section headers linked to valid string-section headers.
- Symbol index 0 and string offset 0 are explicitly synthesized because ELF symbol hash chains use index 0 as the terminator.
- `kw_size[action]` indexing depends on sparse action values up to `KW_STRINGS` and the array being sized as `KW_STRINGS + 1`.
- If the caller buffer is short, `kw_resid` goes negative and later emits are counted but not copied.
- Snapshot consistency depends on the read lock preventing concurrent symbol-table mutation during the sizing and emission passes.

## Research Relevance

For filesystem/storage research, this file is mainly diagnostic infrastructure. Kernel symbol snapshots support debugging, crash analysis, and tooling that may resolve stack traces from allocator, kstat, VFS, or storage subsystems.
