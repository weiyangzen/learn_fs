# File Research: sources/os/linux/linux-stable/fs/squashfs/page_actor.c

## Summary
Implements Squashfs page actors, the abstraction used by block reads and decompressors to write output either to intermediate buffers or directly to page-cache pages.

## Key APIs
- `squashfs_page_actor_init()`.
- `squashfs_page_actor_init_special()`.

## Important Behavior
The cache actor returns a caller-provided array of buffers and has no finish work. The direct actor returns kmapped page-cache pages in index order. When the next expected page is missing, it either returns a temporary buffer if the decompressor requires one, or an error pointer.

The direct actor tracks `next_index`, `returned_pages`, `last_page`, and the current kmap address. Finish unmaps any outstanding page.

## Risks
Callers must not sleep between `squashfs_first_page()` and `squashfs_finish_page()` because direct actors may hold local kmaps. The actor-free path reports an error if not all supplied pages were consumed.
