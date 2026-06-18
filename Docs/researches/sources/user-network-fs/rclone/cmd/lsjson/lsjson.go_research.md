# sources/user-network-fs/rclone/cmd/lsjson/lsjson.go

Purpose: implements `rclone lsjson`, outputting directory/file metadata as JSON, either as an array listing or a single `--stat` item.

Important state/APIs: global `opt operations.ListJSONOpt` and `statOnly`; flags for recursion, hashes, modtime/mimetype suppression, encrypted/original IDs, files-only/dirs-only, metadata, hash type, and stat mode. It delegates to `operations.ListJSON` and `operations.StatJSON`.

Control flow: before creating backends, it mirrors `opt.Metadata` to global config so backend metadata paths are enabled. In stat mode it uses `cmd.NewFsFile`, marshals one item with `json.MarshalIndent`, and prints. Listing mode streams a JSON array manually with comma handling and compact per-item JSON.

State/persistence: read-only remote access and stdout writes. It mutates package/global option state and config metadata flag. Risks include partial JSON output if an error occurs after opening `[`, global `opt` reuse in tests, and backend-specific optional fields. Test signal is likely in operations JSON tests, not this wrapper.
