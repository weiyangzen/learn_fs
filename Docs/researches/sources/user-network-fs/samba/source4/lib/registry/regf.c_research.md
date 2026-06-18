# sources/user-network-fs/samba/source4/lib/registry/regf.c

## Purpose

`regf.c` is Samba's REGF hive backend for Windows NT registry hive files such as `NTUSER.DAT`. It implements `struct hive_operations` over on-disk `regf`, `hbin`, `nk`, `vk`, `sk`, `li`, `lf`, `lh`, and `ri` records generated from `regf.idl`.

## Important APIs, Types, and Functions

`struct regf_data` owns the open file descriptor, parsed header, HBIN array, and throttled write timestamp. `struct regf_key_data` wraps a generic `struct hive_key` with a REGF hive pointer, an HBIN offset, and the parsed `nk_block`. Public entry points are `reg_open_regf_file()` and `reg_create_regf_file()`. Backend operations are implemented by `regf_get_info()`, `regf_get_subkey_by_index()`, `regf_get_subkey_by_name()`, `regf_get_value()`, `regf_get_value_by_name()`, `regf_add_key()`, `regf_del_key()`, `regf_set_value()`, `regf_del_value()`, `regf_get_sec_desc()`, `regf_set_sec_desc()`, and `regf_flush_key()`.

## Control Flow

Opening a REGF file reads the full file, parses and checks the `regf` header, validates the checksum, pulls each HBIN block starting at file offset `0x1000`, and returns the root `nk` as a hive key. Creating a REGF file initializes a header, lazily allocates the first HBIN, writes a root `nk` named `SambaRootKey`, creates a default authenticated-users security descriptor, stores an `sk` block at offset `0x80`, and flushes the file.

Most reads map a logical REGF offset to an HBIN and relative offset with `hbin_by_offset()`, validate the signed cell length in `hbin_get()`, then TDR-pull the typed block. Subkey enumeration and lookup understand direct lists (`li`), first-four-character hash lists (`lf`), base37 hash lists (`lh`), and recursive index lists (`ri`). Value enumeration reads the value-list cell, pulls a `vk_block`, and either returns inline DWORD data from `vk.data_offset` when the high bit is set or returns an HBIN-backed blob.

Writes allocate, resize, or free HBIN cells with `hbin_alloc()`, `hbin_store_resize()`, and `hbin_free()`. Adding a key creates an `nk`, inserts its offset into the parent list in case-insensitive sorted order, updates parent counts, and flushes on the backend's throttle. Deleting a key recursively deletes children and values before removing the key from the parent subkey list. Setting a value updates or creates a `vk`, stores non-DWORD data in an HBIN cell, adjusts the value-list cell, then stores the changed `nk`.

## State and Persistence Behavior

REGF files are held in memory as parsed HBIN blocks and written back wholesale by `regf_save_hbin()`. Saves are throttled to at most once every five seconds unless a flush or destructor requests a forced write. The talloc destructor flushes and closes the file descriptor. Security descriptors are shared through a circular `sk` list with reference counts; `regf_set_sec_desc()` decrements or removes the old descriptor, reuses an equivalent descriptor when found, or appends a new one.

## Dependencies and Integration Points

The backend depends on generated TDR parsers from `regf.idl`, NDR security descriptor push/pull, `winreg` type constants, Samba security helpers, talloc lifetime management, byte-order macros, and low-level file I/O. It plugs into the generic hive API declared in `registry.h`; `tests/hive.c` exercises it alongside the LDB backend, and tools can open REGF files through `reg_open_hive()` or `reg_common_open_file()`.

## Risks and Edge Cases

This backend manipulates a complex binary allocator and several paths have fragile arithmetic. `hbin_store_resize()` compares possible combined free space to `blob.length` rather than the aligned needed size, and the loop starts at the original used cell, so grow-in-place behavior deserves scrutiny. `regf_set_sec_desc()` stores `private_data->nk` using `tdr_push_sk_block` in the final call, which appears inconsistent with the intended NK write. `regf_sl_add_entry()` has a memory check on `lf.hr[lf.key_count].hash` after writing `lf.hr[i].hash`. `ri` list add/delete are explicitly unsupported. Header checksum, dirty/free cell signs, list counts, sorted key order, inline DWORD handling, and security descriptor reference counts are all corruption-sensitive.

## Test Signals

`tests/hive.c` creates REGF hives with minor version 5 and runs add/delete key, recursive delete, value set/get/list/delete, flush, info, and security descriptor round trips. Additional high-value tests should reopen after delayed and forced flush, exercise minor versions 2/3/4/5, add enough subkeys to trigger larger lists, cover `ri` read-only hives, resize values from small to large and back, and validate Windows can load files Samba creates.

Source-read signal: reviewed complete local file (2321 lines).
