# sources/object-store/rustfs/crates/heal/src/heal/utils.rs

`utils.rs` centralizes set disk identifier handling for heal paths. The canonical format is `pool_<pool_idx>_set_<set_idx>`. `format_set_disk_id` formats unsigned indexes, `format_set_disk_id_from_i32` rejects negative endpoint indexes by returning `None`, `normalize_set_disk_id` accepts canonical-looking strings or converts compact `N_M`, and `parse_set_disk_id` validates canonical strings into `(usize, usize)`.

There is no mutable state or persistence. The file only depends on heal `Error`/`Result`. `storage.rs` uses `parse_set_disk_id` to resolve resume disks, and event conversion uses signed-index formatting to avoid panics when endpoint metadata is invalid.

The main risk is that `normalize_set_disk_id` passes through any string starting with `pool_` without validating token count or numeric fields; callers needing validated indexes must call `parse_set_disk_id`. Unit tests cover formatting, signed negative rejection, compact normalization, canonical pass-through, invalid normalization, canonical parsing, and invalid parse errors.
