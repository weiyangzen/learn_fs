# sources/user-network-fs/samba/source4/lib/registry/tools/regdiff.c

## Purpose

`regdiff.c` implements the `regdiff` command, which compares two registry backends and writes a `.reg` diff file or stdout output.

## Important APIs, Types, and Functions

The local `enum reg_backend` distinguishes unknown, local Samba, remote winreg, and null/empty registries. `open_backend()` maps parsed options to `reg_open_samba()`, `reg_open_remote()`, or `reg_open_local()`. `main()` handles command-line parsing and diff generation.

## Control Flow

The command accepts two backend selectors in order: `--local`, `--remote HOST`, or `--null`. After Samba command-line initialization and popt parsing, it opens backend 1 and backend 2, initializes dotreg diff callbacks with `reg_dotreg_diff_save()`, then calls `reg_generate_diff(h1, h2, callbacks, callback_data)`. Errors are printed and exit nonzero.

## State and Persistence Behavior

The command does not mutate the compared registries. It persists the generated diff to `--output` when supplied, otherwise through the dotreg writer's default behavior. Remote backends hold RPC connections for command lifetime, and local backends may create missing local Samba hives during open.

## Dependencies and Integration Points

It uses Samba command-line/loadparm/credentials setup, tevent, popt, registry backends, and dotreg diff callbacks. It is built as a `regdiff` binary with manpage wiring in `wscript_build`.

## Risks and Edge Cases

Exactly two backend selectors are required; missing or extra selectors can result in usage output or ignored state depending on parse order. Only dotreg output is supported here despite the library also supporting PReg save. Error reporting does not include which backend failed beyond the generic message from `open_backend()`.

## Test Signals

Smoke tests should compare null-to-local, local-to-null, and remote-to-local when available, verify output file creation, and apply the generated patch with `regpatch` to confirm semantic correctness. The lower diff engine is covered by `tests/diff.c`.

Source-read signal: reviewed complete local file (182 lines).
