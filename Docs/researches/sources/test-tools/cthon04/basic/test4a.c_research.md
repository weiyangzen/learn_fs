# sources/test-tools/cthon04/basic/test4a.c

Purpose: getattr/lookup-only variant of test4 for repeated stat calls without attribute mutation.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname. Uses dirtree(), stat(), timing helpers, and complete().

Control flow: creates a flat file set, then loops count times over every generated file and calls stat() to ensure it remains visible.

State and persistence: creates files under the selected test directory and leaves them in place.

Dependencies and integration points: shares tests.h defaults and subr.c setup/tree helpers; useful as a lower-mutation comparison to test4.

Risks: summary text multiplies stats by two even though only one stat is performed per file/pass; path buffers are fixed MAXPATHLEN.

Test signals: any missing stat is fatal; success prints stat count and ok marker.
