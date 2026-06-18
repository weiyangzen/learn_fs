# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/facedb.c

Implements face image lookup, file caching, domain translation, and image loading for the `faces` mail notifier.

Key behavior:
- Caches text file reads for `.machinelist` and `.dict` lookups with mtime and short read-time windows.
- `translatedomain()` rewrites domains through regexp entries in `.machinelist`.
- `tryfindpicture()` maps `domain/user` entries in `.dict` to image files.
- `tryfindfiledir()` recursively searches face directories, deferring `48x48x*` directories in preferred depth order and ignoring `512x*`.
- `findfile()` searches `$home/lib/face`, `/lib/face`, parent domains, and unknown fallbacks.
- Maintains a `Facefile` cache for loaded image and mask data.
- `readface()` loads old ascii face files, Plan 9 images, greyscale images, and masks suitable for drawing.
- `findbit()` attaches the resolved image/mask to a `Face`, or creates a yellow fallback tile.

Important implementation details:
- Face cache entries are ref-counted, and deleted entries are retained up to `Nsave` to avoid expensive reloads.
- Greyscale images may be inverted into masks and drawn through black.
- Unknown faces set `f->unknown`, allowing UI overlay of the domain.

Risks and invariants:
- Recursive directory traversal can be expensive, hence the local caches.
- The code assumes `display` is initialized before image-loading paths are used.
