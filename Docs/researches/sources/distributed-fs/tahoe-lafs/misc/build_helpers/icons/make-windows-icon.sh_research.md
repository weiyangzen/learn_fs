# sources/distributed-fs/tahoe-lafs/misc/build_helpers/icons/make-windows-icon.sh

## Purpose

This Bash helper converts SVG icon inputs into Windows `.ico` files. It renders several PNG sizes and combines them with ImageMagick.

## Important APIs, Types, and Functions

The parameter interface is a list of SVG files. Dependencies are `mktemp`, `inkscape`, and ImageMagick `convert`. The resolution set is `16 24 32 48 64 256`.

## Control Flow

With no arguments it prints usage and exits `0`. Otherwise it creates a temp directory, loops over SVG inputs, renders PNGs into a per-icon subdirectory, builds a list of generated PNG paths, calls `convert ... "${f%%.*}.ico"`, and removes the temp directory.

## State, Dependencies, Integration, Risks, and Tests

State is temporary raster files and generated `.ico` outputs. Integration is Windows packaging or icon asset preparation. Risks include `"$*"` collapsing multiple arguments, `${f%%.*}` stripping at the first dot in the whole path, dependency on legacy Inkscape flags, and no `set -e` despite destructive cleanup. Tests should cover multiple SVGs, dotted pathnames, filenames with spaces, and verifying the ICO contains all intended sizes.
