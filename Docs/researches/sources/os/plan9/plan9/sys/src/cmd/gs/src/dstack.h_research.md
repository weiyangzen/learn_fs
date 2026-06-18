# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dstack.h

Purpose: Interpreter dictionary-stack definitions and performance design notes for Ghostscript’s PostScript interpreter.

Key definitions:
- Maps interpreter context fields to shorthand stack macros: `idict_stack`, `d_stack`, `dsbot`, `dsp`, `dstop`.
- Defines stack capacity check macro `check_dstack(n)`.
- Exposes dictionary-stack lookup wrappers such as `dict_find_name_by_index`, `dict_find_name`, and inline/top lookup variants.
- Defines shorthand for dictionary stack state: `min_dstack_size`, `dstack_userdict_index`, `dsspace`, `dtop_*`, `systemdict`.

Design notes:
- The file includes a long architecture note on dictionary lookup performance.
- It describes existing lookup caching around name values, top-dictionary key/value caches, and def-region caches.
- It proposes an improved per-context name lookup cache `C`, restoration stack `R`, per-stack-entry restoration-depth metadata, and dictionary occurrence counts.
- It covers required invalidation/repair behavior for `def`, `put`, `undef`, `restore`, dictionary grow, `begin`, `end`, context switch, access changes, and GC relocation.

Filesystem relevance: None directly. It is core Ghostscript interpreter state machinery, not filesystem code.
