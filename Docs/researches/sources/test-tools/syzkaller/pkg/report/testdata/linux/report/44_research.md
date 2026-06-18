# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/44

Purpose: Linux reporter parse fixture for syzkaller. It expects `kernel BUG in pte_list_remove`, type `BUG`, corrupted `N`, panicked `N`. The log covers a KVM/MMU page-table list removal assertion.

Important APIs, types, and functions: this tests kernel BUG title extraction from a short stack. Key frames include `pte_list_remove`, `drop_spte`, and `mmu_page_zap_pte`.

Control flow: 24 log lines are parsed. The reporter must select the first meaningful BUG frame and avoid marking the short but sufficient report as corrupted.

State and persistence behavior: fixture headers persist expected type/title; runtime parser state is transient.

Dependencies, integration points, risks, and test signals: this protects BUG grouping for KVM MMU page-table teardown. Risks include false corruption or choosing a lower helper. Passing tests require BUG type, exact title, no panic, and corrupted `N`.
