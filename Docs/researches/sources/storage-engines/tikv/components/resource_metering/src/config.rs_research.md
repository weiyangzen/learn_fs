# sources/storage-engines/tikv/components/resource_metering/src/config.rs

## Purpose
`config.rs` defines public resource-metering configuration, validation rules, global network-IO collection state, and online config dispatch to recorder/reporter components.

## Important APIs, Types, And Functions
`Config` is `Serialize`, `Deserialize`, `PartialEq`, and derives `OnlineConfig`. Fields include `receiver_address`, `report_receiver_interval`, `max_resource_groups`, `precision`, and `enable_network_io_collection`. Defaults use no receiver, one-minute reporting, 100 max groups, one-second precision, and network/logical IO collection disabled.

`validate` checks optional receiver address syntax, precision between 100 ms and one hour, `max_resource_groups <= 5000`, and report interval between 500 ms and `precision * 500`. `ENABLE_NETWORK_IO_COLLECTION` is a global `AtomicBool` initialized from the default. `ConfigManager` holds current config and notifiers; `dispatch` applies an online change, validates it, notifies address changes, then notifies recorder and reporter.

## Control Flow
Online config changes arrive as `ConfigChange`. Dispatch clones current config, applies the change through generated `update`, validates the candidate, emits address notification if needed, sends the full new config to recorder and reporter notifiers, and commits it as current.

## State And Persistence Behavior
`ConfigManager` stores the current in-memory config. The global `ENABLE_NETWORK_IO_COLLECTION` is atomic process state consumed by collection paths elsewhere. Persistent storage is external to this file.

## Dependencies And Integration Points
The file integrates with `online_config`, serde, `tikv_util::config::ReadableDuration`, recorder and reporter config notifiers, and `AddressChangeNotifier` from reporter single-target code.

## Risks
Validation error messages say "between 0 and MAX" for max groups but only enforces an upper bound. Dispatch notifies recorder/reporter after address notification; downstream notifier failures are not represented in this API. Global atomic state can diverge from `ConfigManager.current_config` if other modules update it independently.

## Test Signals
`test_config_validate` covers default validation, valid address/config, too-large reporting interval, too-large group count, and invalid precision.
