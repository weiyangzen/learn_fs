<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.c -->
# sources/security-integrity/keyutils/keyctl.c

## Purpose

`keyctl.c` is the command-line frontend for Linux kernel key retention service operations. It maps subcommands to libkeyutils wrappers and syscalls for creating keys, keyrings, reading payloads, changing ownership and permissions, searching, linking, unlinking, instantiating requested keys, Diffie-Hellman computation, public-key operations, keyring restriction, moving keys, capability probing, recursive cleanup, and watch/test extension entry points.

## Important APIs, Types, and Functions

The central command table binds names such as `add`, `padd`, `request`, `request2`, `update`, `newring`, `revoke`, `clear`, `link`, `unlink`, `search`, `read`, `pipe`, `print`, `list`, `describe`, `session`, `instantiate`, `negate`, `reject`, `purge`, `invalidate`, `dh_compute`, `dh_compute_kdf`, `restrict_keyring`, `pkey_*`, `move`, `supports`, `watch*`, and `--test` to noreturn action functions. Shared helpers include `do_command()` for prefix/exact command dispatch, `format()` for usage, `error()` for perror-and-exit, `get_key_id()` for numeric/special/name lookup parsing, `hex2bin()` for optional hex payload conversion, `grab_stdin()` for pipe payloads, `calc_perms()` for effective permission display, `read_file()` for pkey inputs, and `dump_key_tree()`/`dump_key_tree_aux()` for recursive keyring rendering.

## Control Flow

`main()` delegates to `do_command()`, which consumes the program name, finds an unambiguous command match, and invokes the action. Each action validates argument count, converts key IDs with `get_key_id()`, invokes the relevant libkeyutils function, prints IDs or formatted payloads where appropriate, and exits. Recursive commands use `recursive_session_key_scan()` callbacks to unlink, reap, or purge keys. DH and pkey commands allocate output buffers based on kernel-reported lengths or pkey query limits before emitting hex/binary output. `session` and `new_session` change process/session keyring state and then exec a shell or target program.

## State and Persistence Behavior

The file has no durable storage of its own; it mutates kernel keyrings through `add_key()`, `request_key()`, and `keyctl()` operations. Key material can be read from argv, stdin, or files; sensitive buffers are wiped where explicit conversions or DH outputs are handled. Process state includes cached effective UID/GID/group data for permission display, the `verbose` flag, and command-local allocations. Kernel state changes include key creation/update/revocation/invalidation, keyring links, ownership/permission changes, restriction application, persistent keyring retrieval, and session keyring joins.

## Dependencies and Integration Points

The program depends on `keyutils.h` for kernel constants and wrappers, `keyctl.h` for command declarations shared with watch/testing modules, Linux syscall availability, `/proc/keys` lookup via library helper code, and libc process/file APIs. It integrates with `keyctl_watch.c` through watch subcommands and `keyctl_testing.c` through `--test`. It is the primary executable exercised by the shell tests under `tests/keyctl`.

## Risks and Edge Cases

Command prefix matching is convenient but can become ambiguous when new names share prefixes. `grab_stdin()` hard-limits stdin payloads to 1 MiB, while request-key pipe handling elsewhere has a smaller payload buffer. Some numeric parsing uses `strtoul()` without full range validation beyond trailing characters. Pkey encrypt/decrypt allocate buffers using query fields that must match kernel semantics; a mismatch can truncate or fail operations. Recursive traversal depth limits prevent unbounded recursion but may hide deeper trees. Name lookup via `%type:desc` ultimately depends on `/proc/keys` visibility and description parsing.

## Test Signals

The mapped tests cover bad/no-arg handling, add/padd/pupdate payload paths, keyring clear/list/describe/read, ID parsing, instantiation failures, invalidation, link and move recursion, duplicate link semantics, request-key callouts, keyring restrictions, and revoke errors. Feature tests exercise DH vectors, built-in trusted keyrings, and kernel limit probes.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.c -->
