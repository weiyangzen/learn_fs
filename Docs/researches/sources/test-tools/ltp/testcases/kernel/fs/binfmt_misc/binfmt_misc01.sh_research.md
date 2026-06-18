# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc01.sh

Purpose: LTP regression test that invalid binfmt_misc registration strings fail and do not create usable binary type entries. It includes offset-overflow coverage for a historical kernel bug.

Important APIs/types/functions: `TST_CNT=9`, `TST_TESTFUNC=do_test`, `verify_binfmt_misc`, `get_binfmt_misc_mntpoint`, `remove_binary_type`, `tst_res`, `tst_run`, shell `echo` to `$mntpoint/register`, `cat`, `awk`, and `which cat`.

Control flow: each test case builds one invalid registration string: bad delimiter/format, invalid type, slash in name, slash in magic/extension, invalid negative or huge offset, and invalid flags. `verify_binfmt_misc` writes the string to the register file and passes only if registration fails and no entry file exists. If an entry is created, it reads it with `cat` to trigger potential kernel issues, reports failure, and removes the entry.

State/persistence behavior: may transiently create binfmt_misc entries under the mounted binfmt_misc filesystem, then removes them.

Dependencies/integration: sources `binfmt_misc_lib.sh`, requiring root, mounted or loadable binfmt_misc, LTP shell harness, and `cat`.

Risks/test signals: failure messages indicate invalid input was accepted. Registration-name extraction with colon delimiters depends on string shape, so adding new malformed cases should preserve cleanup ability.
