# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/425

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING in pvr2_i2c_core_done`, type `WARNING`, corrupted `N`, panicked `Y`. The body covers sysfs group removal warning during PVR2 I2C adapter teardown.

Important APIs, types, and functions: this tests warning extraction in media/I2C teardown. Frames include `sysfs_remove_group`, `dpm_sysfs_remove`, `device_del`, `device_unregister`, `i2c_del_adapter`, and `pvr2_i2c_core_done`.

Control flow: 62 log lines are parsed. The warning originates in sysfs but should be attributed to the PVR2 I2C cleanup path; panic-on-warn sets the panicked flag.

State and persistence behavior: headers persist parser expectations; runtime state is read-only and temporary.

Dependencies, integration points, risks, and test signals: this protects deduplication for media USB/I2C cleanup warnings. Risks are title selection from sysfs/device helpers. Passing tests require warning type, panic `Y`, non-corrupted state, and the PVR2 cleanup title.
