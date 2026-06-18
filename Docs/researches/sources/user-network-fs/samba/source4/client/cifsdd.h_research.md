# sources/user-network-fs/samba/source4/client/cifsdd.h

Purpose: declares shared argument, statistics, and IO abstraction types for the `cifsdd` utility.

Important APIs/types: `enum argtype` and `struct argdef` describe dd-style options. `set_arg_argv()`, `set_arg_val()`, and `check_arg_*()` expose argument storage. `struct dd_stats_record` holds full/partial block and byte counters. `dd_seek_func`, `dd_read_func`, `dd_write_func`, and `struct dd_iohandle` abstract local or SMB IO. Flags define EOF, direct IO, sync IO, write mode, and oplock. `dd_open_path()`, `dd_fill_block()`, and `dd_flush_block()` are core IO helpers implemented elsewhere.

Control flow/integration: `cifsdd.c` configures args and opens handles through this interface; lower-level IO code provides local or SMB implementations behind function pointers.

State/dependencies: declares global `PROGNAME` and `dd_stats`; runtime state is held in IO handles and counters. Forward declares Samba client option/session/event/GENSEC-related types so the header stays lightweight.

Risks/test signals: the IO contract relies on implementations setting `DD_END_OF_FILE` and updating counters consistently. `io_flags` mixes capability/configuration bits with EOF state. Exercised by `cifsdd` CLI/integration tests and lower-level IO tests.
