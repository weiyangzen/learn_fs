# sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-osx-icon.sh

## Purpose

This Bash helper converts SVG icon inputs into macOS `.icns` files. It renders multiple PNG sizes into an `.iconset` directory and asks `iconutil` to build the final icon.

## Important APIs, Types, and Functions

The script has no functions. Its parameters are SVG paths. It uses resolution array `16 32 64 128 256 512 1024`, `inkscape` for rasterization, hard links or moves for retina `@2x` names, and `iconutil -c icns`.

## Control Flow

With no arguments it prints usage and exits successfully. Otherwise it creates `temp` under the current directory, loops over SVG inputs, renders all base sizes, constructs expected Apple iconset filenames, runs `iconutil`, and finally removes `temp`.

## State, Dependencies, Integration, Risks, and Tests

State is a temporary `./temp` tree and generated `.icns` files in the caller's working directory. Dependencies are Bash, Inkscape's legacy CLI options, and macOS `iconutil`. Risks include iterating over `"$*"` instead of `"$@"`, collisions in `./temp`, overwriting outputs, and hard-link failures across filesystems. Test signals are SVG fixtures with spaces in filenames, existing `temp`, and validation that generated `.icns` contains expected icon sizes.
