# File Research: sources/local-fs/xfsprogs/libxfs/defer_item.h

Header for libxfs deferred operation adapters.

Key responsibilities:
- Declares defer-add entry points for bmap, attr, exchange maps, extent free, rmap, and refcount intents.
- Defines attr defer operation enum.
- Declares log intent space calculation helpers.

Dependencies:
- Used by libxfs transaction and metadata update paths.

Notable risks:
- Interfaces expose kernel-like deferred operation concepts without exposing actual log intent objects.
