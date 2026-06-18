# sources/test-tools/lcov/bin/genpng

## Purpose

`genpng` creates a compact PNG overview of a source or `.gcov` file by mapping each source character to one pixel. Its primary use is visual coverage navigation: covered, uncovered, uninstrumented, highlighted, and differential categories receive different foreground/background colors.

The script can be executed as a command-line tool or loaded by another Perl script. When loaded, it exposes `genpng_process_file()` and `gen_png()`.

## Important APIs, types, and functions

- `check_and_load_module("GD")` dynamically checks for the required `GD` Perl module and exits with code 2 when unavailable.
- Command options are parsed with `Getopt::Long`: `--tab-size`, `--width`, `--output-filename`, `--dark-mode`, `--help`, and `--version`.
- `genpng_process_file($filename, $out_filename, $width, $tab_size, $dark)` reads either plain text or `.gcov` text and converts it to internal `<count>:<source>` lines.
- `gen_png($filename, $show_tla, $dark, $width, $tab_size, @source)` builds the `GD::Image`, allocates color palettes, expands tabs, maps line tags/counts through `lcovutil::pngMap`, paints pixels, and writes PNG bytes.
- Colors for differential TLA categories come from `lcovutil` hashes `%tlaColor` and `%tlaTextColor`.

## Control flow

On direct command-line execution, `genpng` loads `GD`, parses options, validates the source filename, chooses a default output name of `<source>.png`, and calls `genpng_process_file()`. For `.gcov` input, the reader recognizes common gcov line forms: uninstrumented lines, zero-count lines, and positive-count lines. For plain text, every line is treated as uninstrumented.

`gen_png()` creates an image with width equal to the requested overview width and height equal to the number of source lines, falling back to one empty line for empty inputs. For each source line it expands tabs, parses an optional tag and execution count, chooses foreground/background colors, paints each non-space character with text color and each space with background color, truncates at image width, fills the rest of the row, and writes a binary PNG.

## State and persistence behavior

There is no long-lived state. The persistent result is the output PNG file. The function keeps only local image/color variables and a one-line memory of the previous instrumented line so uninstrumented continuation lines can inherit the prior coverage color region. It reads the full source into memory before rendering.

## Dependencies and integration points

`genpng` depends on Perl `GD`, `Getopt::Long`, `File::Basename`, `Cwd`, `FindBin`, and the shared LCOV `lcovutil` module. It integrates with `.gcov` text produced by gcov and with differential coverage metadata encoded as LCOV/HTML TLA tags. Other LCOV tools can `do` or require this script and call `gen_png()` directly.

## Risks and edge cases

- Missing `GD.pm` is a hard runtime dependency failure.
- The `.gcov` parser is regex-based and supports expected gcov text forms only; unexpected spacing or newer formats may silently skip lines.
- Width is not validated for positive values in this script, so invalid or tiny widths rely on GD/runtime behavior.
- The tab expansion formula is hand-written and affects pixel alignment against genhtml source views.
- Output height equals line count, so very large source files can allocate large images.
- The function dies on unknown PNG tags unless `lcovutil::pngMap` contains them.

## Test signals

Tests should cover `--help`, `--version`, missing filename, missing GD behavior in a controlled environment, plain-text rendering, `.gcov` rendering for uninstrumented/covered/uncovered lines, dark mode, tab expansion, width truncation, empty source files, and tagged differential inputs. A basic assertion can confirm a PNG signature is written and dimensions match width by line count.
