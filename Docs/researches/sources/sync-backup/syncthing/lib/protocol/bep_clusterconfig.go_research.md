## sources/sync-backup/syncthing/lib/protocol/bep_clusterconfig.go

Purpose: typed Go representation and wire conversion for BEP cluster configuration messages.

Important types/functions: `Compression`, `FolderType`, `FolderStopReason` constants; `ClusterConfig` with `toWire` and `clusterConfigFromWire`; `Folder` with `toWire`, `folderFromWire`, `Description`, `LogAttr`, and `IsRunning`; `Device` with `toWire` and `deviceFromWire`.

Control flow and state: conversion functions allocate slices and recursively convert folders/devices to generated protobuf `bep` types. `Folder.IsRunning` treats paused as not running and all other reasons as running. Logging helpers return structured folder identity.

Dependencies and integration points: used during connection cluster-config exchange, index sender pause decisions, encrypted password token propagation, introducer behavior, and remote device metadata.

Risks: nil wire folders/devices are not guarded except top-level cluster config nil. Adding BEP fields requires updating conversions or data will be dropped. `DeviceID(w.Id)` assumes valid byte length from wire.

Test signals: request index sender pause/startup tests indirectly exercise cluster config behavior.
