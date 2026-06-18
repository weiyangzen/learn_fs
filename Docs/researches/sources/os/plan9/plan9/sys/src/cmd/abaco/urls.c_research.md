# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/urls.c

URL object management and webfs-backed URL opening for Abaco.

Key responsibilities:
- Allocates, duplicates, reference-counts, and frees `Url` objects.
- Opens `webfs` clone files, writes requested URL commands, writes POST bodies when needed, opens response body files, and reads content type/parsed URL attributes.
- Canonicalizes path components by removing empty, `.`, and resolvable `..` elements.
- Combines base and relative URLs, including protocol-relative, absolute-path, query, fragment, and sibling-path forms.

Dependencies:
- Uses Plan 9 webfs file hierarchy under `webmountpt`.
- Uses `Runestr`, `HGet`/`HPost`, `copyrunestr`, `validurl`, and rune string helpers.

Notable risks:
- `urlcombine` is explicitly marked as a hack and mutates temporary portions of the base string while finding query boundaries.
- Error handling calls `error` for some failures but returns `-1` for others.
