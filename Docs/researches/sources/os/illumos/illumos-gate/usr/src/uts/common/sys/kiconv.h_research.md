# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv.h

## Role

`kiconv.h` defines the kernel iconv framework interfaces and internal data structures for registering and dispatching codeset conversions. Its substantive content is compiled only under `_KERNEL`.

## Major Definitions

`kiconv_code_list_t` maps normalized code names to numeric IDs. `kiconv_conv_list_t` maps a to-code/from-code pair to a module ID and conversion function pointers: open, streaming conversion, close, and string conversion. `kiconv_mod_list_t` stores module names and reference counts.

Module registration uses `kiconv_ops_t` entries, each naming a to-code/from-code pair and conversion callbacks, and `kiconv_module_info_t`, which supplies module name, conversion table, aliases/canonicals, and `nowait` behavior. `kiconv_data_t` is the conversion descriptor returned to framework consumers, storing an implementation handle and conversion-list index. `kiconv_state_data_t` stores common conversion state including an ID and whether a BOM has been processed.

The file also defines compact table component types for conversions to UTF-8 and to single-byte encodings, maximum normalized code-name length, skippable characters during code-name normalization, ASCII and UTF-8 replacement characters, and numeric module IDs for embedded, Japanese, simplified Chinese, Korean, traditional Chinese, and EMEA conversion modules.

## Interfaces

Kernel functions include `kiconv_init()`, module registration/unregistration, and module reference-count query.

## Integration Notes

The header defines a plug-in style conversion registry whose function pointers are loaded by module ID. Code-name normalization ignores `-`, `_`, `.`, and `@`, so aliases must be designed with that behavior in mind. Replacement-character policy mirrors `iconv(3C)` behavior for non-identical characters and depends on the target codeset.
