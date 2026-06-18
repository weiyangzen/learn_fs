# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/38

Purpose: Minimal OpenBSD suppressed panic fixture for a broken-pipe disconnect. Expected title is `panic: vop_generic_bclient_loop: send disconnect: Broken pipe`, expected type `DoS`, and `SUPPRESSED: Y`.

Important parser APIs and patterns: the generic `panic:` title path captures the panic text. `ctorOpenbsd` has suppression `panic:.*send disconnect: Broken pipe`, which marks this report suppressed.

Control flow: the raw body contains only `panic: vop_generic_bclient_loop: send disconnect: Broken pipe`. There is no DDB output or stack.

State and persistence: static minimal fixture. It represents a crash-like console line caused by an SSH/client disconnect condition that syzkaller should suppress.

Dependencies and integration: validates OpenBSD suppression configuration in `ctorOpenbsd`, plus generic panic detection when no stack is available.

Risks: if suppressions are changed, infrastructure disconnects could become user-visible bugs. If the parser required stack frames, this suppression case might be missed and handled as lost connection elsewhere.

Test signals: exact title and `SUPPRESSED: Y`; no stack required.
