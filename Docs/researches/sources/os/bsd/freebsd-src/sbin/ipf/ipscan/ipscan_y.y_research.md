# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/ipscan_y.y

This file is both the yacc grammar and command implementation for `ipscan`, an IPFilter application-layer/content scan rule loader.

The grammar parses `start`, `start-group`, and `content` rules. Rules bind a tag to client/server byte patterns, optional masks, and an action: `close`, `track`, or `redirect`, with optional `else` action. It also supports variable assignment through the shared lexer variable system.

`cram()` decodes quoted pattern strings with C-style escapes and octal escapes into fixed-size scanner text/mask buffers. `addtag()` constructs an `ipscan_t`, validates mask lengths, maps parsed actions to scanner constants, and submits add/remove ioctls (`SIOCADSCA`/`SIOCRMSCA`) unless dry-run is active. Redirect actions are parsed but reported unsupported.

`showlist()` queries scanner stats with `SIOCGSCST`; in list mode it walks scanner entries through `kmemcpy()`, otherwise prints counters.

The `main()` function handles file loading, listing, stats, remove, dry-run, debug, and verbose options, opens `IPL_SCAN`, and repeatedly invokes `yyparse()` for file inputs.

Important dependencies include `ipf.h`, `opts.h`, `kmem.h`, `netinet/ip_scan.h`, `ipscan_l.h`, and shared lexer functions.

Implementation notes and risks:
- The parser and CLI are global-state driven (`opts`, `fd`, `yyin`).
- `makepair()` allocates a two-pointer array but parsed strings are not consistently freed after rule construction.
- Redirect syntax exists but the implementation logs it as unsupported.
- Scanner listing depends on kernel memory access for entry traversal.
