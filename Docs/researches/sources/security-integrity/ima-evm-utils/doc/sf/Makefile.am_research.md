# sources/security-integrity/ima-evm-utils/doc/sf/Makefile.am

## Purpose
Automake rules for generating the SourceForge wiki HTML document.

## Important APIs, Types, And Functions
- `noinst_DATA = sf-wiki.html` builds the HTML without installing it.
- `sf-wiki.html: sf-wiki.md` runs pandoc from markdown to HTML.
- `CLEANFILES` removes generated HTML.

## Control Flow
Recursive make invokes pandoc when `sf-wiki.md` is newer than the generated HTML.

## State And Persistence
Writes `sf-wiki.html` in the doc/sf build directory.

## Dependencies And Integration Points
Depends on pandoc and the source markdown file.

## Risks And Edge Cases
No install target means generated HTML is build artifact only. Pandoc output can vary by version.

## Test Signals
Signal is successful generation and cleanup of `sf-wiki.html`.
