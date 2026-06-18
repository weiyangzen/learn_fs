# sources/sync-backup/kopia/internal/ospath/ospath_nonwindows.go

Purpose: non-Windows filename helper.

Important APIs/types/functions: `SafeLongFilename`.

Control flow: returns the input filename unchanged because POSIX paths do not need the Windows long-path prefix.

State and persistence behavior: stateless.

Dependencies and integration points: callers can use one API without OS checks.

Risks and test signals: only build-tag selection matters; Unix tests should assert identity behavior.
