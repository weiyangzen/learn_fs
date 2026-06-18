# sources/sync-backup/syncthing/lib/config/metrics.go

## sources/sync-backup/syncthing/lib/config/metrics.go

Purpose: Exposes static configuration information as Prometheus metrics.

Important APIs/types/functions: `RegisterInfoMetrics` registers collector funcs for `folderInfoMetric` and `folderDeviceMetric`. Descriptors emit `syncthing_config_folder_info` labels for folder ID/label/type/path/paused and `syncthing_config_device_info` labels for device ID/name/introducer/paused/untrusted.

Control flow and state: On collection, the metrics read current wrapper snapshots via `FolderList` and `DeviceList`, emitting gauge value `1` for each folder/device. Registration uses `prometheus.DefaultRegisterer.MustRegister`.

Dependencies and integration: Depends on Prometheus client and the `Wrapper` interface. It integrates config state with monitoring without persisting anything.

Risks and test signals: Label cardinality is proportional to configured folders/devices and includes folder paths/device names, which may expose sensitive metadata. `MustRegister` panics on duplicate registration. No direct tests in this subset.
