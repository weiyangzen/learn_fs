# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.c

`common.c` provides shared Plan 9 PostScript translator support. It defines a character escaping table, page-list selection, page/string emission helpers, page accounting, file concatenation through Bio, checked reallocation, and formatted error reporting.

`startstring()`/`endstring()` batch text into PostScript strings with positioning. `startpage()`/`endpage()` emit DSC page markers, `save`/`restore`, and `showpage` when the current page is selected. `pageon()` also temporarily suppresses debug output for skipped pages.
