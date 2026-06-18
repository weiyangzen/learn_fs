# sources/user-network-fs/samba/source3/registry/reg_parse_dox.cfg

## Purpose
`reg_parse_dox.cfg` is the Doxygen configuration for the registry import/export parser and formatter documentation set.

## Important APIs, Types, And Functions
The config names the project `Registry Import / Export`, optimizes output for C, extracts all documented and static symbols, and includes the parser/formatter/import files plus related `net_registry`, `cbuf`, and `srprs` sources. It enables HTML and LaTeX output, warnings, todo/test/bug/deprecated lists, preprocessing, include graphs in settings, and source-file listings. It does not enable XML, RTF, man, or dot processing.

## Control Flow
Doxygen consumes this file when run with the local compile command `doxygen reg_parse_dox.cfg`. Input is non-recursive and explicitly listed, so newly related files are invisible until added. Output directories use defaults except HTML under `html` and LaTeX under `latex`.

## State And Persistence
The file persists documentation-generation settings, not runtime registry state. Generated documentation is build output and depends on the local Doxygen version and source tree.

## Dependencies And Integration Points
It integrates with Doxygen 1.6-era settings and references local source files by relative name. The footer has editor local variables and a compile command.

## Risks And Test Signals
Because `INPUT` is explicit and relative, running from the wrong directory or renaming files breaks documentation generation. `HAVE_DOT = NO` means graph-related options are mostly inert. Tests/signals are a successful Doxygen run with warnings reviewed, expected HTML/LaTeX outputs present, and confirmation that all import/export sources intended for docs are in `INPUT`.
