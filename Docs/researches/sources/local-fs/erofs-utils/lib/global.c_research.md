# File Research: sources/local-fs/erofs-utils/lib/global.c

## Purpose
Library-global initialization and cleanup wrapper for configuration, curl, XML parser, and compression workqueue state.

## Important Functions
- `liberofs_global_init()`: locks a global mutex, initializes `cfg`, optionally initializes libxml parser for S3, and initializes curl once.
- `liberofs_global_exit()`: locks, exits MT compression workqueue, cleans curl/libxml state, exits config, and unlocks.

## Interactions
- Calls `erofs_init_configure()` / `erofs_exit_configure()`.
- Calls `z_erofs_mt_global_exit()` to tear down compression workqueue state.
- Conditional on `HAVE_LIBCURL` and `S3EROFS_ENABLED`.

## Notes
Curl initialization is protected by a static boolean and mutex.
