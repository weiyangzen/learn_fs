# File Research: sources/virtualization/libblockdev/src/lib/plugins.c

## Role
Implements `BDPluginSpec` boxed-type helpers for plugin selection and GObject introspection/binding support.

## API Behavior
- `bd_plugin_spec_copy()`:
  - returns NULL for NULL input;
  - allocates a new `BDPluginSpec`;
  - copies the enum value;
  - duplicates `so_name`.
- `bd_plugin_spec_free()`:
  - returns on NULL;
  - frees `so_name` and the struct.
- `bd_plugin_spec_new()`:
  - constructs a new spec from plugin enum and optional soname;
  - duplicates the soname when provided.
- `bd_plugin_spec_get_type()`:
  - lazily registers `BDPluginSpec` as a static boxed GType;
  - uses the copy/free functions above.

## Important Detail
`BDPluginSpec.so_name` is declared `const gchar *` in the public struct, but this implementation duplicates and frees it. The comment notes this mismatch and preserves current allocation behavior.

## Dependencies and Interactions
- Used by public initialization APIs in `blockdev.c.in`.
- GType registration supports language bindings and introspection users that need boxed plugin specs.

## Filesystem/Storage Relevance
This is generic plugin-selection plumbing. It lets callers request specific storage plugins, such as Btrfs or LVM, and optionally force a specific plugin shared-object name.
