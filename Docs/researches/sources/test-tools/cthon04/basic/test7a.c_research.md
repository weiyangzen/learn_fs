# sources/test-tools/cthon04/basic/test7a.c

Purpose: rename-only correctness and timing variant.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/nname. Uses rename(), stat(), dirtree(), rmdirtree(), timing helpers.

Control flow: creates files, then repeatedly renames each file to the new prefix and back, verifying after each rename that the old name is gone and the new/current name is stat-able.

State and persistence: temporary names exist only within each iteration; cleanup removes the generated original-name files afterward.

Dependencies and integration points: narrower companion to test7 for filesystems without hard-link support concerns.

Risks: does not test overwrite rename cases; generated names use fixed buffers; failures leave partial renamed state for cleanup.

Test signals: success prints the number of renames and complete(); any failed stat/rename exits nonzero.
