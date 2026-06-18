# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/movie.c

This file implements a dictionary backend for a tagged movie database.

Key behaviors:
- Defines tag IDs for fields such as title, author, cast, director, release date, country, running time, rating, video data, awards, abstract, and text paragraphs.
- `movieprintentry()`:
  - For `r`, writes the raw entry.
  - Prints title first for normal/headword output.
  - For `h`, stops after the title.
  - For full output, formats release metadata, video, authors, director, producer, cinematography, credits, cast, awards, notes, abstracts, and text paragraphs.
- `movienextoff()` finds the next entry by scanning for a line beginning `$$`.
- `movieprintkey()` prints “No key”.
- `moutall()` emits comma-separated repeated tag values.
- `moutall2()` formats values of form `field1_field2` as `field2 (field1)`, with a special case for Himself/Herself cast entries.
- `mget()` finds a tag value and continuation lines within an entry.

Notable implementation details:
- Entry parsing assumes tag lines begin with two-character tags and a following separator, with continuation lines beginning with space.
- There is a literal output typo: `Cinematograpy`.
