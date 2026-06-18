# sources/test-tools/cthon04/basic/test2.c

Purpose: removal counterpart for the create test; verifies unlink/rmdir behavior over a generated tree.

Important APIs/types/functions: parses -h, -t, -f, -n and tree shape/name arguments. Uses mtestdir(), system("test1 -s ...") for setup when needed, rmdirtree(), starttime(), endtime(), complete().

Control flow: after argument validation, the program tries to chdir into the test directory. If absent, it invokes test1 in silent mode with the same shape parameters, then retries. It times rmdirtree() over the tree and prints removal totals.

State and persistence: removes generated files/directories beneath the selected test directory. It does not remove the test directory itself; it clears known generated names.

Dependencies and integration points: depends on the test1 executable being discoverable by system() when the tree is missing, and on subr.c for traversal/removal policy.

Risks: setup command is built with sprintf into a 256-byte buffer and includes user-provided names; mismatched parameters can leave extra files that make rmdir fail.

Test signals: success is a removal count line followed by complete(); failures identify the current directory via error().
