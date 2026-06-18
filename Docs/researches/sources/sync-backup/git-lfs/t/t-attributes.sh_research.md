# sources/sync-backup/git-lfs/t/t-attributes.sh

## Purpose
Tests Git LFS handling of Git attribute macros, including macros in repository, subdirectory, and global attribute files. It checks both whether files are actually cleaned into LFS objects and whether `git lfs track` recognizes already-supported patterns.

## Important APIs, Functions, and Control Flow
The four tests cover top-level macros, nested macros, global `$HOME/.config/git/attributes`, split macro definitions across HOME and repo `.gitattributes`, and unspecified macro flags with `!lfs`. They create files, commit them, assert local LFS object presence or absence, then inspect `git lfs track` output.

## State, Persistence, and Dependencies
The script mutates `.gitattributes`, subdirectory `.gitattributes`, and global attributes in `$HOME/.config/git/attributes`. It depends on Git's `check-attr` semantics, `assert_local_object`, `refute_local_object`, and `calc_oid`.

## Integration Points, Risks, and Test Signals
The main integration is between Git's attribute macro resolution and Git LFS's own attribute parser. Comments document known limitations where `git lfs track` reads attribute files depth-first and therefore does not fully match Git's macro resolution in nested cases. Signals are object-store assertions and `"already supported"` messages. Risks are global attribute pollution and platform-dependent HOME handling.
