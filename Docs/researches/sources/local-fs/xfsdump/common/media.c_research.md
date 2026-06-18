# File Research: sources/local-fs/xfsdump/common/media.c

## Role

This file selects and initializes the media strategy used by xfsdump/xfsrestore and creates one `media_t` manager descriptor per drive stream.

It sits between the drive layer and media strategy implementations.

## Strategy Selection

The file declares two external strategies:

- `media_strategy_simple`
- `media_strategy_rmvtape`

`media_create()` builds generic media descriptors for every drive, lends them to each strategy in precedence order, and selects the first strategy whose `ms_match()` callback accepts the current command line and drive setup.

## Media Label Handling

For dump builds, `media_create()` scans command-line options for a media label option and rejects duplicates or missing values. If none is provided, it uses an empty label.

Each write media header receives the selected label and, for dump builds, a new media UUID. Restore builds clear the media UUID.

## Initialization Flow

After strategy selection:

- The chosen strategy is assigned to each `media_t`.
- Each media write header receives the selected strategy ID.
- `ms_create()` is called for full strategy initialization.
- `media_init()` and `media_complete()` dispatch to strategy callbacks.

## Header Bridging

`media_get_upper_hdrs()` returns pointers to:

- global read/write headers
- media-header upper-layer read/write buffers
- their sizes

This lets upper layers place their own headers inside the media header reserved area.

## Allocation

`media_alloc()` obtains read/write media-header storage from `drive_get_upper_hdrs()`, verifies expected sizes, records drive/header pointers in `media_t`, sets the media label, and initializes the media ID.
