# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/getsubopt.c

Read completely: 116 lines.

Implements `getsubopt()`. It parses a comma/space/tab-separated suboption string in place, splits optional `name=value` pairs by writing NUL terminators, updates `*optionp` for the next call, sets `*valuep`, and stores the current token in global `suboptarg`.

It returns the matching token index from the supplied token vector or `-1` for no match/end. Because it modifies the input string, callers must pass mutable storage.
