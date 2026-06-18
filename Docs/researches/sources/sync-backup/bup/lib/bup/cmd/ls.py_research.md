# sources/sync-backup/bup/lib/bup/cmd/ls.py

## Purpose
`cmd/ls.py` is a thin CLI adapter around `bup.ls`, listing repository VFS paths.

## APIs and Control Flow
`main(argv)` flushes stdout, wraps it as a byte stream, delegates all option parsing and listing behavior to `ls.via_cmdline(argv[1:], out=out)`, and exits with the returned code. The local file intentionally points readers to `lib/bup/ls.py` for the actual option specification.

## State, Dependencies, Integration, Risks, Tests
The command is read-only and persists nothing. Its dependencies are just `bup.ls` and `byte_stream`, but it is integrated wherever users expect `bup ls` and where `ftp.do_ls` reuses lower-level `bup.ls` functions. Risks are wrapper-level minimal: stdout byte behavior and correct exit-code propagation. Test signals should focus on delegation, flushing, returned status via `sys.exit`, and ensuring the wrapper does not alter argv semantics.
