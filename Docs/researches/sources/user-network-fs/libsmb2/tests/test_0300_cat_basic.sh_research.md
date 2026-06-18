<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0300_cat_basic.sh -->
# sources/user-network-fs/libsmb2/tests/test_0300_cat_basic.sh

Purpose: Basic file-read integration test for async cat helper.

Important APIs, types, and functions: Runs `./prog_cat "${TESTURL}/CAT"` and uses shared `failure`.

Control flow: Reads a known remote file named `CAT` and discards output.

State and persistence behavior: No local persistence. Remote file must preexist.

Dependencies and integration points: Depends on SMB share fixture containing `CAT`.

Risks: Fixture-dependent and does not compare content, only successful read completion.

Test signals: Direct async read/cat pass/fail signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0300_cat_basic.sh -->
