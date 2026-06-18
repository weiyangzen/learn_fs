# File Research: sources/os/plan9/9front/sys/src/cmd/dict/movie.c

Adapter for `/lib/movie/data` records.

Key elements:
- Defines two-letter movie data tags such as title, release date, country, cast, director, awards, abstract, and text.
- `movieprintentry` prints title for headword mode, raw data for `r`, and formatted metadata for normal printing.
- Handles repeated tags with comma-separated list rendering.
- `moutall2` rewrites `field1_field2` as `field2 (field1)`, with special handling for “Himself/Herself”.
- `movienextoff` finds the next record beginning with `$$`.
- `mget` finds tag values, including continuation lines.

Dependencies:
- Uses common output helpers from `utils.c`.

Research notes:
- The same data file is indexed three ways in `utils.c`: title, actor, and director.
