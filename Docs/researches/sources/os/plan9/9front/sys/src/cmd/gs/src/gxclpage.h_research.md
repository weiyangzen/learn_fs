# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.h

Declares saved-page command-list operations for Ghostscript printer devices.

Key behavior:
- Declares `gdev_prn_save_page`, which packages the current page in a banding printer device into caller-provided `gx_saved_page` storage.
- Declares `gdev_prn_render_pages`, which renders an array of placed saved pages through a compatible printer device.
- Documents that saved pages may be retained in memory or written elsewhere by the client.
- Documents render placement semantics: each saved page’s origin is translated to its specified offset, but Y offset must currently be zero.
- Notes required compatibility between saved pages and the rendering device, including buffer space and band width.

Dependencies:
- Requires `gdevprn.h` and `gxclist.h` for printer and saved-page types.
- Includes `gxclio.h` for command-list file abstractions.

Research notes:
- This header exposes a higher-level page composition API over the lower-level command-list band files.
