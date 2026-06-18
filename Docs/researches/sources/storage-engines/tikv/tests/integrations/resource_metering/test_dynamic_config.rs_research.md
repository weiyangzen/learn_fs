# sources/storage-engines/tikv/tests/integrations/resource_metering/test_dynamic_config.rs

Purpose: validates live resource metering config updates: receiver address, report interval, max resource groups, precision, and network I/O collection.

Important APIs and functions: `TestSuite::cfg_receiver_address`, `cfg_report_receiver_interval`, `cfg_max_resource_groups`, `cfg_precision`, `cfg_enable_network_io_collection`, workload helpers, `alloc_port`, and `ENABLE_NETWORK_IO_COLLECTION`.

Control flow: `test_enable` toggles receiver address from empty to valid to empty to valid. `test_report_interval` changes reporting from 3s to 1s and measures inter-arrival times. `test_max_resource_groups` creates skewed tags and expects overflow grouped under `""` after reducing the limit. `test_precision` checks timestamp spacing before and after changing precision. `test_enable_network_io_collection` toggles the global network I/O flag.

State and persistence: mutates `ConfigController` resource metering state, reporter connection state, in-memory aggregation, and a global atomic. Storage is used only to generate tagged workload.

Dependencies and integration: `resource_metering::ConfigManager`, single-target reporting, mock receiver, dynamic config plumbing, aggregation policy, and global collection switch.

Risks: timing-sensitive interval/precision assertions; receiver reconnects can leak records across phases; skewed tag aggregation depends on workload distribution.

Test signals: runtime config changes take effect without restart and affect record emission, aggregation, precision, and network I/O collection.
