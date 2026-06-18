# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kiconv.c

## Role

`kiconv.c` implements committed kernel iconv interfaces: `kiconv_open(9F)`, `kiconv(9F)`, `kiconv_close(9F)`, and `kiconvstr(9F)`. It provides embedded UTF-8 conversions for common single-byte encodings and dynamically loads regional conversion modules for broader codepage support.

## Embedded Conversions

Embedded conversions cover UTF-8 to and from:
- CP1252
- ISO-8859-1
- ISO-8859-15
- CP850

UTF-8 to single-byte conversions use state objects with a mapping-table ID and BOM-processing flag. They validate UTF-8 using `u8_number_of_bytes`, `u8_valid_min_2nd_byte`, and `u8_valid_max_2nd_byte`, binary-search mapping tables, copy ASCII directly, and use `?` for non-identical conversions.

Single-byte to UTF-8 conversions use table lookup for bytes above `0x7f`, copy ASCII directly, and reject unmapped code points unless string-mode replacement is requested.

## String Conversion

`kiconvstr_to_sb()` and `kiconvstr_fr_sb()` provide one-shot conversions with flags:
- `KICONV_IGNORE_NULL` controls whether NUL terminates processing.
- `KICONV_REPLACE_INVALID` converts invalid input to replacement characters instead of failing.

UTF-8 replacement uses `U+FFFD`; single-byte replacement uses the ASCII replacement character.

## Code Names And Modules

`normalize_codename()` removes skippable characters, folds ASCII uppercase to lowercase, and maps aliases through `code_list`.

`conv_list` contains embedded conversions plus module-backed conversions for Japanese, Simplified Chinese, Korean, Traditional Chinese, and EMEA encodings. Module rows start with function pointers set to `NULL`.

`check_and_load_conversions()` normalizes names, locates the conversion row, loads the corresponding `kiconv` module with `modload()` if needed, increments the module function-use refcount, and returns a descriptor.

`kiconv_register_module()` fills conversion function pointers during module install. `kiconv_unregister_module()` clears them only when the module refcount is zero.

## Public Interface

`kiconv_open()` opens a conversion and rolls back the module refcount if the module’s open routine fails.

`kiconv()` dispatches through the selected conversion function.

`kiconv_close()` calls the conversion close routine, frees the descriptor, and decrements the module refcount.

`kiconvstr()` loads/refs a conversion, calls the string converter, frees the temporary descriptor, and decrements the module refcount.

## Research Notes

The main correctness surface is buffer accounting and UTF-8 validation. Audit hotspots are binary-search assumptions about sorted mapping tables, descriptor ID bounds, module refcount lifetime, `modload()` races, invalid-input replacement paths, and ensuring every output path updates remaining input/output lengths consistently.
