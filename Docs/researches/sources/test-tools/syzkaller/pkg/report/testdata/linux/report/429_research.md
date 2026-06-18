# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/429

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: ODEBUG bug in blk_mq_unregister_disk`, type `WARNING`, corrupted `N`, panicked `Y`. The report is a debugobjects warning during block multiqueue disk unregister.

Important APIs, types, and functions: this tests ODEBUG warning parsing in block-device teardown. Frames include `debug_print_object`, `debug_object_init`, `init_timer_key`, `kobject_release`, `kobject_put`, and `blk_mq_unregister_disk`.

Control flow: 78 log lines are parsed. Debugobjects emits the warning; panic-on-warn follows; stack selection must identify the block MQ unregister operation.

State and persistence behavior: expected output is persisted in headers. Parser state is in-memory only.

Dependencies, integration points, risks, and test signals: this protects block-layer crash grouping for timer/debugobject lifetime bugs. Risks include choosing kobject or timer helpers. Passing tests require exact ODEBUG title, warning type, panic `Y`, and no corruption.
