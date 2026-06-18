# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncnameprov.c

## Purpose

`ncnameprov.c` implements NameChanger’s Filter Manager name-provider callbacks. It rewrites generated names and normalized path components so callers above the filter receive user-mapping names even when the underlying filesystem object lives under the real mapping.

## Functions

- `NcGenerateFileName` handles opened, normalized, and short name generation. It queries lower providers without requesting from the current provider to avoid recursion, parses the lower name, determines pre-open vs opened case sensitivity, compares the lower name against the real mapping, and returns either the lower name or a constructed user-mapping name.
- For opened/normalized names, opened objects inside the real mapping are translated to the user mapping with `NcConstructPath`.
- For short-name requests, an exact real-mapping match returns the configured user short final component directly; otherwise the function queries the lower provider’s short name.
- `NcNormalizeNameComponentEx` supports normalized-name component expansion. It translates parent directories inside the user mapping to the real mapping before opening/enumerating, handles the user mapping’s parent plus mapping final component specially, calls `NcQueryDirectoryFile`, and if the real component was queried returns the user long final component in the expansion buffer.

## Integration

The callbacks are registered through `nc.c` name-provider glue. They depend on instance mapping context, path overlap classification, internal create helper, and directory-query support.

## Risks and Notes

Pre-open name generation is deliberately marked `FLT_FILE_NAME_DO_NOT_CACHE` to avoid poisoning lower name caches before NameChanger’s create redirection has run. The component-normalization path has comments noting that only specific return codes should be used if name construction should continue.
