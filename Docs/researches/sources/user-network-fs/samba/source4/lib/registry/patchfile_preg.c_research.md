# sources/user-network-fs/samba/source4/lib/registry/patchfile_preg.c

## Purpose

`patchfile_preg.c` implements import and export of Windows Group Policy `Registry.pol` PReg patch files through Samba's registry diff callback interface. It serializes registry diff operations as UTF-16 bracketed records after a `PReg` header and parses those records back into generic add, set, delete-value, delete-all-values, and delete-key callbacks.

## Important APIs, Types, and Functions

`struct preg_data` carries the output file descriptor and talloc context used by save callbacks. `reg_preg_diff_save()` creates the writer callback table. `reg_preg_diff_load()` parses an existing PReg stream. Internal helpers `preg_read_utf16()` and `preg_write_utf16()` convert one UTF-16 code unit or a UTF-8 string to the on-disk encoding. Callback implementations include `reg_preg_diff_set_value()`, `reg_preg_diff_del_key()`, `reg_preg_diff_del_value()`, `reg_preg_diff_del_all_values()`, and `reg_preg_diff_done()`.

## Control Flow

Saving opens the requested file or stdout, writes the `PReg` magic and version 1 header, and returns callbacks consumed by `reg_generate_diff()`. Normal value updates write `[key;value;type;length;raw-data]` with UTF-16 delimiters but raw value bytes. Delete operations are represented with policy marker names such as `**Del.<name>`, `**DelVals.`, and `**DeleteKeys`.

Loading validates the eight-byte header, then loops record by record. It reads an opening `[`, key path, value name, binary type, binary length, binary data, and closing `]`, then translates special marker values into deletion callbacks or emits `add_key` plus `set_value` for ordinary entries. The loader closes the supplied file descriptor and frees its temporary talloc context at exit.

## State and Persistence Behavior

The file persists only the generated PReg patch stream. It does not directly mutate a registry; mutation happens only when the parsed callbacks are an apply callback set. Save-side cleanup closes the writer fd in `done()`. Load-side state is transient except that parsed callbacks may update the caller's registry. Delete-key export currently writes one `**DeleteKeys` value per deletion rather than accumulating multiple deletes as the FIXME notes.

## Dependencies and Integration Points

This file depends on `registry.h` for `struct reg_diff_callbacks`, `WERROR`, and `DATA_BLOB`, on generated winreg type constants, and on Samba byte-order/sys_rw helpers. It is wired into the `registry` library by `wscript_build` and used by `reg_diff_load()`, `reg_diff_apply()`, tests in `tests/diff.c`, and any tool that asks for PReg diff save/load.

## Risks and Edge Cases

Input parsing uses a fixed 1024-byte scratch buffer and does not grow for long key or value names. If `length >= buf_size`, the current data read is skipped but `data_blob_talloc()` still copies from the previous scratch buffer, which is a malformed-input risk. Several delimiter checks combine negation and bounds tests in a fragile way. `reg_preg_diff_del_key()` assumes the key path contains a backslash and repeatedly recomputes `strrchr()`, so top-level delete paths could misbehave. The format writes host memory through helper macros but still relies on correct little-endian handling for type and length.

## Test Signals

`tests/diff.c` creates two LDB-backed registries, saves a PReg diff through `reg_preg_diff_save()`, generates a diff, applies it, and verifies the expected HKLM path exists. Additional useful coverage would include long key/value names, large binary data, missing delimiters, grouped `**DeleteValues` and `**DeleteKeys`, top-level key delete attempts, and round trips against real Windows `Registry.pol` files.

Source-read signal: reviewed complete local file (387 lines).
