# sources/sync-backup/casync/test/test-caformat.c

Purpose: tests archive format encoding/decoding helpers and constants.

Important APIs/types/functions: main constructs format structures, validates magic/feature/digest serialization, and checks expected values through `assert_se`.

Control flow/state: local-only test with no persistent files. It exercises conversion helpers rather than full archive traversal.

Dependencies/integration: includes `caformat.h` and util assertions, providing a low-level guard for on-disk format compatibility.

Risks/test signals: important because format regressions can break existing archives. Coverage is limited to cases hard-coded in the test.

Source research group: `subset-b-009122`.
