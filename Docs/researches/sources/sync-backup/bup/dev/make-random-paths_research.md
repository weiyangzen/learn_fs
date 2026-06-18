# sources/sync-backup/bup/dev/make-random-paths

## Purpose
Generates random byte-named files for path encoding and traversal stress tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `randint`, `re` invalid-fragment filtering, `fsencode`, `get_argvb`, and `open`.

## Control Flow
Parses `NUM DEST_DIR`, repeatedly creates 1 to 32 byte random names excluding NUL, slash, dot, and `..`, and writes empty files until count is reached.

## State and Persistence Behavior
Creates files in the destination directory.

## Dependencies and Integration Points
Used by `dev/configure-sampledata` when randomized sampledata paths are enabled.

## Risks and Test Signals
Risks are collisions, invalid path bytes on a filesystem, and unseeded randomness. Signal is the requested number of created files or error.
