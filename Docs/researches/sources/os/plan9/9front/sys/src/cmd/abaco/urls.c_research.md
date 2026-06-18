# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/urls.c

URL object allocation, webfs opening, canonicalization, and relative URL combination for Abaco.

Key responsibilities:
- Allocates/refcounts/frees/duplicates `Url` objects.
- Opens URLs through webfs clone/control/body files, including POST bodies.
- Reads content type and parsed/actual URL attributes from webfs.
- Canonicalizes path components after `://`, resolving empty, `.`, and `..` elements.
- Combines base and relative URLs, including scheme-relative, absolute-path, query, fragment, and path-relative cases.

Important behavior:
- `urlopen()` writes `url <src>` to a webfs connection and returns an open body fd.
- If parsed URL is missing, actual URL falls back to source URL.
- POST body is written before opening the response body.
- `urlcombine()` duplicates already-valid absolute URLs.

Dependencies:
- Uses global `webmountpt`, rune helpers, `validurl()`, and Plan 9 webfs layout.

Notable risks:
- `getattr()` sets `Runestr.nr` to byte count rather than rune count; ASCII metadata works, but non-ASCII metadata can be inconsistent.
- `urlcanon()` mutates the URL string in place while splitting components.
