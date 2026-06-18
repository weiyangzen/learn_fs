# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/426

Purpose: Linux reporter parse fixture for syzkaller. It also expects `WARNING in pvr2_i2c_core_done`, type `WARNING`, corrupted `N`, panicked `Y`. This companion fixture covers a similar sysfs group removal warning through an I2C client unregister path.

Important APIs, types, and functions: relevant frames include `sysfs_remove_group`, `dpm_sysfs_remove`, `device_del`, `device_unregister`, `__unregister_client`, `i2c_del_adapter`, and `pvr2_i2c_core_done`.

Control flow: 62 log lines are parsed. The parser must normalize a slightly different call chain to the same PVR2 cleanup title, preserving deduplication across teardown variants.

State and persistence behavior: persistent state is textual fixture data; parser state is temporary title/type/flag selection.

Dependencies, integration points, risks, and test signals: this pairs with report 425 to protect stable grouping despite variant stack tails. Risks include splitting the same bug by selecting `__unregister_client` in one fixture. Passing tests require the same expected warning title and panic behavior.
