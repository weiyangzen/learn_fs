<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadinfo.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadinfo.h

## Purpose
This header declares locale-dependent catalog lookup support shared by alias expansion, locale name parsing, fallback filename construction, and domain loading.

## Important APIs, Types, and Functions
It defines `PATH_SEPARATOR`, locale component flags (`CEN_REVISION`, `CEN_SPONSOR`, `CEN_SPECIAL`, `XPG_NORM_CODESET`, `XPG_CODESET`, `TERRITORY`, `CEN_AUDIENCE`, `XPG_MODIFIER`), combined masks, and `struct loaded_l10nfile`. It declares `_nl_normalize_codeset`, `_nl_make_l10nflist`, `_nl_expand_alias`, `_nl_explode_name`, and `_nl_find_language`.

## Control Flow
No runtime flow is present. The header documents the contract: `_nl_explode_name` destructively splits mutable locale names and `_nl_make_l10nflist` creates cached lookup results and successor lists.

## State and Persistence
It defines the shape of cached lookup state: filename, decided flag, loaded data pointer, next link, and flexible successor array.

## Dependencies and Integration Points
Included by `gettextP.h`, `explodename.c`, `l10nflist.c`, and related domain lookup code. It bridges locale parsing and catalog loading.

## Risks
The bitmask constants encode fallback semantics, so changes must stay synchronized across parser and fallback builder. `successor[1]` is a flexible-array idiom requiring exact allocation sizing.

## Test Signals
Compile and run lookup tests that cover all mask bits, successor array allocation, and path separator handling on Unix and Windows-like platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadinfo.h -->
