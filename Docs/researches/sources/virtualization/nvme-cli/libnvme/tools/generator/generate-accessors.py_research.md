# File Research: sources/virtualization/nvme-cli/libnvme/tools/generator/generate-accessors.py

This is libnvme’s generator for struct accessors, lifecycle helpers, linker-script entries, SWIG fragments, and optional Python dict-field tables. It parses annotated C headers and emits committed generated files such as `accessors.h`, `accessors.c`, `accessors.ld`, `accessors.i`, and dict-table headers.

Annotation model:
- `// !generate-accessors[:read=MODE,write=MODE]` enables getter/setter generation for a struct. Modes are `generated`, `custom`, or `none`.
- `// !access:read=...,write=...` overrides member access modes.
- `const` members force `write=none`.
- `// !nested-accessors[:...]` marks helper structs whose fields can be flattened into parent accessors via `// !access:nested`.
- `// !generate-lifecycle` emits `struct_new()` and `struct_free()`.
- `// !lifecycle:none` excludes a member from destructor freeing.
- `// !default:VALUE` emits an init-defaults helper and default assignment logic.
- `// !generate-python[:alias=NAME]`, `// !python:none`, and `// !python:alias=NAME` drive SWIG output.
- `// !generate-dict-table` and `// !dict-table:none` drive field-offset table generation.

Parsing:
- Uses regexes for simple C struct bodies, char arrays, scalar arrays, generic members, and nested struct members.
- Supports:
  - dynamic `char *`
  - `char **` string arrays
  - fixed `char name[N]`
  - fixed scalar arrays
  - scalar value fields
  - selected integer/bool/string fields for dict tables
- Does not support typedef struct and is limited by `STRUCT_RE`, which matches `struct name { ... };` without nested braces.

Generated C/header behavior:
- Dynamic string setters free the old value and `strdup()` the new value or clear on NULL.
- Fixed char-array setters use `snprintf()` into the destination array.
- String-array setters deep-copy NULL-terminated arrays and free the previous array.
- Scalar setters assign directly.
- Scalar-array setters use `memcpy()`.
- Getters return stored values or pointers.
- Lifecycle constructors allocate zeroed structs, optionally call init-defaults, and return `-EINVAL`/`-ENOMEM` on setup errors.
- Destructors free owned `char *` and `char **` members, then free the struct.
- Linker output lists generated getters, setters, lifecycle functions, and default initializers under `LIBNVME_ACCESSORS_3`.

SWIG/Python behavior:
- Emits a `_nvme_guarded_setattr` helper to reject unknown Python attributes.
- Direct generated members appear as struct fields.
- Custom accessors are routed through `%extend` and `%rename` bridge macros.
- Read-only members emit `%immutable`.
- Nested flattened fields are excluded from SWIG direct struct output because SWIG cannot access dotted field paths as plain members.
- Detects Python alias collisions and invalid struct aliases before writing.

Dict-table behavior:
- Emits `struct fctx_field { const char *key; size_t off; }` arrays grouped by int, long, bool, and `char *`.
- Skips unsupported narrow scalars, arrays, const fields, structs, and complex pointers, warning unless explicitly silenced.

Main program:
- CLI options include `--h-out`, `--c-out`, `--ld-out`, `--swig-out`, `--dict-table-out`, `--nested-source`, `--prefix`, and `--verbose`.
- Expands globbed header inputs.
- Pass 1 collects nested-accessor structs across normal and nested-source headers.
- Pass 2 parses header structs and accumulates header/source/ld/SWIG fragments.
- Emits files with generated banners, include guards, forward declarations, and required includes.

Integration:
- `tools/generator/meson.build` invokes this through `update-accessors.sh`.
- Generated files are committed and checked for drift rather than regenerated during normal builds.

Risk and maintenance notes:
- Regex C parsing is adequate for the project’s annotated private headers but fragile for complicated declarations, preprocessor-heavy struct bodies, nested braces, function pointers, or unsupported pointer types.
- Fixed char-array setter generation does not guard NULL input; callers must not pass NULL for those setters.
- Dynamic string default initialization uses `strdup()` without checking allocation failure.
- The generator hardcodes the linker version section name `LIBNVME_ACCESSORS_3`; manual version-script policy is handled by the wrapper script.
