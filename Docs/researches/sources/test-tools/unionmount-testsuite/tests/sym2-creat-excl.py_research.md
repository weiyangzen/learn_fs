# sources/test-tools/unionmount-testsuite/tests/sym2-creat-excl.py

Purpose: checks `O_CREAT|O_EXCL` through an indirect symlink chain pointing to an existing file. It should fail without modifying either link or target.

Important APIs and functions: five subtests use `ctx.indirect_sym()`, `ctx.direct_sym()`, `ctx.reg_file()`, and `ctx.open_file()` with exclusive create flag combinations.

Control flow: each case attempts to open the indirect symlink with `crt=1, ex=1`, expects `EEXIST`, then reads through the indirect link to confirm original content.

State and persistence: both the direct symlink, indirect symlink, and target file remain unchanged. No writes should be committed after the failed exclusive create.

Dependencies and integration: depends on the harness constructing an indirect symlink chain and on VFS semantics for exclusive create through symlinks.

Risks: symlink chains plus exclusive create are sensitive to whether the final target exists; broken fixture setup would change expected errno.

Test signals: `EEXIST` on every exclusive open and stable target content `:xxx:yyy:zzz`.
