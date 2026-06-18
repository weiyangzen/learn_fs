# sources/test-tools/unionmount-testsuite/tests/sym1-creat.py

Purpose: checks ordinary `O_CREAT` opens through a direct symlink to an existing file, including overwrites and appends.

Important APIs and functions: five subtests use `ctx.direct_sym()`, `ctx.reg_file()`, and `ctx.open_file()` with read-only, write-only, append, and read/write modes.

Control flow: read-only opens confirm existing content. Write and read/write cases write `q` then `p` at offset zero or append them, with follow-up reads proving expected content transitions.

State and persistence: the target file content changes through the symlink. Overwrite cases modify the first byte; append cases extend the file.

Dependencies and integration: depends on symlink following during open and harness content checking. It interacts with overlay copy-up if the lower target is modified.

Risks: tests assume write offset starts at zero for non-append opens and that `O_CREAT` does not replace the symlink itself.

Test signals: final content strings `pxxx:yyy:zzz` or `:xxx:yyy:zzzqp` prove writes reached the target through the symlink.
