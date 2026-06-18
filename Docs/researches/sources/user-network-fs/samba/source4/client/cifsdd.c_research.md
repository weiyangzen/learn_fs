# sources/user-network-fs/samba/source4/client/cifsdd.c

Purpose: main program for `cifsdd`, a dd-like copy utility that can read/write local paths or SMB UNC paths using Samba client libraries.

Important APIs/functions: argument helpers manage dd-style options; `copy_files()` performs block copying; `open_file()` applies direct/sync/oplock/write flags and delegates to `dd_open_path()`; `print_transfer_stats()` and `dd_handle_signal()` provide dd-like runtime behavior; `main()` initializes Samba command-line state, parses popt plus dd options, validates input/output, installs signal handlers, and runs the copy.

Control flow: defaults set 4096-byte block sizes, unlimited count, zero skip/seek, and no IO flags. Popt parses Samba options, remaining `name=value` args configure dd options, and `bs=` updates both `ibs` and `obs`. Copying allocates a buffer twice the larger block size, opens input/output handles, seeks by block counts, loops until SIGINT/count/EOF, fills enough input for an output block with `dd_fill_block()`, flushes output with `dd_flush_block()`, and prints stats. SIGUSR1 prints stats and continues.

State/dependencies/integration: global `dd_stats` records counters; signal counters are globals. Uses Samba cmdline/popt, loadparm SMB client options, resolver, GENSEC settings, tevent, and IO abstractions from `cifsdd.h`.

Risks/test signals: `count` default and multiplication can overflow with extreme block sizes; seek return values are ignored; path strings are process-lifetime allocations; signal counters are not `sig_atomic_t`. Client integration tests such as `test_cifsdd.sh` likely cover behavior.
