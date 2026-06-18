## sources/sync-backup/kopia/icons/convert.sh

Purpose: shell utility for generating Kopia app, tray, and site icon assets from source artwork.

Important APIs/types/functions: `make_icns`, `make_ico`, calls to `sips`, `iconutil`, ImageMagick `convert`, and `cp`.

Control flow, state, and persistence: `set -e` aborts on failure. macOS `.icns` generation creates a temporary `MyIcon.iconset`, resizes multiple icon dimensions, converts it, removes the temp directory, and moves output. Windows `.ico` generation uses ImageMagick auto-resize. The script writes assets under app and site resource directories.

Dependencies and integration points: depends on macOS `sips`/`iconutil` and ImageMagick. Integrated into manual/release asset workflows rather than Go runtime.

Risks and test signals: unquoted variables and fixed temp directory `MyIcon.iconset` can fail with spaces or concurrent runs. There are no automated tests; validation is visual/asset-existence oriented.
