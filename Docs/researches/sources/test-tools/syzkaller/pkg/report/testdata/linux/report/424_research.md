# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/424

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in chaoskey_disconnect`, alternate `bad-access in chaoskey_disconnect`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The report covers hardware RNG unregister and kthread stopping during ChaosKey USB disconnect.

Important APIs, types, and functions: this tests KASAN UAF-read parsing around refcount helpers. Key frames include `refcount_inc_not_zero_checked`, `refcount_inc_checked`, `kthread_stop`, `hwrng_unregister`, `chaoskey_disconnect`, and `usb_unbind_interface`.

Control flow: 89 log lines are parsed. The crash begins at refcount/KASAN helpers, but the title must identify the USB disconnect callback.

State and persistence behavior: expected parser output is stored in headers. Runtime state is transient KASAN and frame-selection metadata.

Dependencies, integration points, risks, and test signals: this protects syzkaller grouping for hardware RNG USB teardown. Risks include misclassifying as a refcount warning instead of KASAN UAF or selecting `hwrng_unregister`. Passing tests require UAF-read type, exact title/alternate, and no panic/corruption.
