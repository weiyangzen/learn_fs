# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/408

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: refcount bug in input_register_device`, type `REFCOUNT_WARNING`, corrupted `N`, panicked `Y`. The log covers input device registration hitting `refcount_inc` on zero through kobject parent acquisition.

Important APIs, types, and functions: this file is static Linux report testdata. It exercises syzkaller report parsing APIs and Linux refcount warning title extraction. Important stack frames include `refcount_inc`, `kobject_get`, `get_device_parent.isra.27`, `device_add`, and `input_register_device`.

Control flow: the test reads the headers, parses 80 log lines, sees the warning at `lib/refcount.c:153`, and verifies the title points at the input registration operation. The kernel path is an input-device add path ending in a panic after warning.

State and persistence behavior: expected parser output is persisted in the text headers. Runtime state is limited to parser match state, report slices, selected frame, and flags.

Dependencies, integration points, risks, and test signals: this protects refcount-warning classification for input subsystem crashes used by syzkaller dashboard grouping. Risks include mapping the title to `refcount_inc` or `device_add` instead of `input_register_device`. Test success requires the refcount crash type, panicked flag, non-corruption, and stable crash boundary extraction.
