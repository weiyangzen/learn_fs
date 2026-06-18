# sources/sync-backup/rsync/define-from-md.awk

## Purpose
Extracts documented default value lists from markdown manpage content and writes a generated C header define, currently for default compression suffixes or CVS ignore patterns depending on `hfile`.

## Important APIs, Types, and Functions
The caller passes `-v hfile=NAME` and a markdown input. The script chooses `DEFAULT_DONT_COMPRESS` with `*.` prefixes when `hfile` contains `compress`, otherwise `DEFAULT_CVSIGNORE`. It scans indented quote/list lines matching `^    > [^ ]+$`, strips backticks, accumulates `$2`, and writes `#define ... "..."` to `hfile`.

## Control Flow
`BEGIN` selects the define name and prefix. Matching list lines extend `value_list`. Sentinel conditions stop after `.gz` for compression or `SCCS` for CVS ignore. Any nonmatching line resets `value_list`, making the extraction dependent on contiguous documented lists. `END` writes the generated header or exits with failure if no list was found.

## State and Persistence Behavior
Writes exactly one generated header file named by `hfile`. No other persistent state is maintained.

## Dependencies and Integration Points
Depends on AWK and stable markdown formatting in rsync manpage sources. The generated constants feed runtime defaults for compression exclusions and CVS-style ignore handling.

## Risks and Test Signals
Risks include fragile markdown pattern matching, accidental extraction from the wrong list, sentinel drift, and shell invocation from an unexpected directory. Test signals include regenerating the target headers after manpage edits, checking the defines compile, and verifying defaults match documented lists.
