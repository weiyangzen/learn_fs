
# sources/user-network-fs/rclone/backend/hdfs/hdfs.go

## Purpose
This file registers the HDFS backend and defines its user-facing configuration schema for non-Plan 9 platforms.

## Important APIs, Types, And Control Flow
`init` registers `fs.RegInfo{Name: "hdfs"}` with `NewFs` and options for `namenode`, `username`, Kerberos `service_principal_name`, Kerberos `data_transfer_protection`, and path `encoding`. `Options` is the parsed config struct consumed by `NewFs` in `fs.go`. `xPath` normalizes HDFS paths by forcing a leading slash and joining root with a tail path.

## State And Persistence
This file has no runtime persistence beyond global backend registration. Configuration values are persisted by rclone's normal config system, not by this file.

## Dependencies And Integration Points
It depends on rclone `fs`, `config`, and `encoder`. The `Options` fields are used by the HDFS client construction and path conversion in `fs.go` and `object.go`.

## Risks And Test Signals
The `namenode` option is required and sensitive, and examples imply comma-separated HA NameNode addresses. `xPath` uses `path.Join`, so empty roots and dot-like components are normalized; tests should cover root/tail combinations, especially remote roots without a leading slash. Platform build tags mean this file is excluded on Plan 9.
