# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms.c

Read completely: 1618 lines.

Implements in-kernel ELF symbol table management and the `/dev/ksyms` interface. It tracks the base kernel and module symbol tables, supports symbol lookup by name/address, maintains DTrace name maps when enabled, publishes tables to lockless/pserialized readers, and presents a coherent snapshot ELF image to userland for read/mmap/ioctl consumers.

Core state:
- `struct ksyms_symtab` entries are held in both `ksyms_symtabs` tail queue for writers/snapshots and `ksyms_symtabs_psz` pslist for pserialized readers.
- `kernel_symtab` stores the base kernel table.
- `ksyms_hdr`, `ksyms_symsz`, `ksyms_strsz`, and `ksyms_ctfsz` describe the synthesized user-visible ELF image.
- `ksyms_lock`, `ksyms_cv`, `ksyms_snapshotting`, and `ksyms_snapshot` serialize module changes and snapshot creation/reuse.
- `struct ksyms_snapshot` stores a refcounted UVM anonymous object, size, device, generation, and max symbol-name length for one coherent `/dev/ksyms` view.

Initialization and loading:
- `ksyms_init()` optionally loads a copied boot symbol table from `db_symtab` when `COPY_SYMTAB` is enabled, initializes the lock/CV, and creates the pserialize domain.
- `ksyms_addsyms_elf()` validates an ELF image, finds `SHT_SYMTAB` and its string table, optionally finds `.SUNW_ctf`, initializes the synthesized ELF header, and adds the base kernel table.
- `ksyms_addsyms_explicit()` supports platforms that directly know symbol/string table addresses.
- `ksyms_verify()` reports missing symbol/string tables in diagnostic/debug kernels and refuses loading absent tables.

Symbol table packing and lookup:
- `addsymtab()` filters unusable symbols when DTrace is not enabled, copies/compacts symbols to a new location, normalizes non-absolute section indices to `SHBSS`, tracks maximum symbol-name length and min/max symbol addresses, sorts globals before locals and by name, builds DTrace original-to-new symbol maps, publishes the table at `splhigh()`, recalculates aggregate sizes, and marks ksyms loaded.
- `findsym()` binary-searches sorted global symbols and, unless external-only lookup is requested, linearly searches local symbols.
- `ksyms_getval()` and `ksyms_getval_unlocked()` look up a symbol value with pserialize protection.
- `ksyms_get_mod()` returns a module symtab by name for callers that already guarantee module lifetime.
- `ksyms_mod_foreach()` iterates symbols for a module under `ksyms_lock`.
- `ksyms_getname()` finds the nearest symbol at or below an address, with filters for procedure/object/any and exact-match options.

Module integration:
- `ksyms_modload()` allocates a new symtab and DTrace name map, adds it under `ksyms_lock`, and invalidates any cached snapshot.
- `ksyms_modunload()` finds the module table, waits for active snapshot creation, removes it from both queues at `splhigh()`, waits for a pserialize grace period, recalculates sizes, invalidates the snapshot, and frees the name map and symtab.
- DDB-only `ksyms_sift()` searches and prints matching symbols, with optional type markers.

Synthesized ELF image and snapshots:
- `ksyms_hdr_init()` copies the loaded ELF header and rewrites program/section header metadata for a synthetic image containing `.note.netbsd.ident`, `.symtab`, `.strtab`, `.shstrtab`, fake `.bss`, and optional `.SUNW_ctf`.
- `ksyms_sizes_calc()` walks all tables, adjusts `st_name` offsets to concatenate string tables for userland, and recomputes aggregate symbol/string sizes.
- `ksyms_snapshot_alloc()` creates a refcounted snapshot object backed by `uao_create()`.
- `ksyms_take_snapshot()` writes the ELF header, all symbol tables up to a captured last table, all string tables, and base-kernel CTF data into the snapshot UVM object.
- `ksymsopen()` validates device/minor and loaded state, allocates a file, reuses an existing cached snapshot or becomes the single snapshotting LWP, creates/fills/caches a new snapshot, and returns a cloned file using custom fileops.

`/dev/ksyms` file operations:
- `ksymsread()` reads from the snapshot UVM object, serializing shared `f_offset` updates with the file lock, rejecting negative offsets, and returning EOF at or past snapshot size.
- `ksymsmmap()` permits read-only mappings within the rounded snapshot size by referencing the UVM object.
- `ksymsseek()` implements `SEEK_SET`, `SEEK_CUR`, and `SEEK_END` with overflow and negative-offset checks.
- `ksymsstat()` reports a character-device-like stat structure with size and generation.
- `ksymsioctl()` supports old and current value/symbol lookup ioctls plus total-size query.
- `ksymsclose()` releases the snapshot reference.
- `ksyms_cdevsw` only uses device open; all subsequent operations are on the cloned fileops.

Concurrency and invariants:
- Readers that traverse live symtabs use pserialize; unload waits for a grace period before freeing.
- Queue publication/removal happens at `splhigh()` so DDB should not see an inconsistent queue state.
- Module unload waits for snapshot creation to finish before removing tables.
- Snapshot readers use immutable UVM objects, so later module loads/unloads invalidate only the global cached snapshot, not open file views.

Risks and notes:
- `KSYMS_MAX_ID` bounds the startup static DTrace name map; excess symbols are truncated with an error message.
- Comments note TODOs for mmap/poll even though this version implements fileops mmap, suggesting the TODO is stale or refers to device-level behavior.
- `ksyms_getname()` scans all symbols linearly within candidate modules.
