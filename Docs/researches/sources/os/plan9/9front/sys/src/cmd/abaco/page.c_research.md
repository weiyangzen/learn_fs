# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/page.c

Page loading, image loading/cache, frames, rendering, selection, scrolling dispatch, refresh metadata, and page lifecycle for Abaco.

Key responsibilities:
- Loads pages asynchronously through webfs and `uhtml`, then parses HTML/plain text with libhtml.
- Loads and caches images through MIME-specific filter pipelines.
- Handles framesets by recursively creating child `Page` objects from `Kidinfo`.
- Closes/aborts pages and recursively frees documents, layouts, children, images, titles, and refresh state.
- Renders pages into page rectangles and child frame rectangles.
- Handles page mouse and keyboard input, including links/forms, text selection, and scrollbars.
- Extracts selected page text to snarf.
- Parses meta-refresh URL/time and triggers refresh reloads.

Important behavior:
- Empty content type is treated as HTML.
- Unsupported non-text MIME types become status errors.
- Image cache entries are refcounted and shared by source URL.
- `pageabort()` recursively marks aborting and waits while `loading` is nonzero.
- `pageredraw()` renders into a global temporary image, then copies to the screen.

Dependencies:
- Uses webfs, external filters (`uhtml`, image decoders, `resize`), libhtml parser, layout/draw code, URL helpers, and refresh channel.

Notable risks:
- Page loading and UI refresh share mutable `Page` fields across procs with limited locking.
- `loadimg()` returns partially initialized `Cimage` objects on error for placeholder rendering.
- `pageabort()` busy-waits in 100 ms intervals until loader clears state.
