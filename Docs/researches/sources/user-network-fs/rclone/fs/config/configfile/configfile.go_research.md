# sources/user-network-fs/rclone/fs/config/configfile/configfile.go

Purpose: implements `config.Storage` using an INI-like file via `goconfig`, with encrypted load/save support, auto-reload on external changes, symlink-aware atomic replacement, and mutex protection.

Important APIs/types/functions: `Install` installs `&Storage{}` into config. `Storage` stores a mutex, `*goconfig.ConfigFile`, and last file info. Internal methods `_check` and `_load`; public methods `Load`, `Save`, `Serialize`, `HasSection`, `DeleteSection`, `GetSectionList`, `GetKeyList`, `GetValue`, `SetValue`, and `DeleteKey`.

Control flow: `_check` stats the current config path and reloads if mtime or size changed. `_load` opens the config path, maps not-found to `config.ErrorConfigFileNotFound`, decrypts with `config.Decrypt`, and loads goconfig data; a defer guarantees an empty config object exists on errors. `Save` resolves symlinks, creates the config dir, writes serialized and encrypted data to a temp file, syncs and closes it, preserves existing file mode where possible, attempts group ownership copy on Unix, creates a backup temp file, renames old config to backup, then renames the new temp file into place and updates cached file info.

State and persistence behavior: all access locks `Storage.mu`. Data is persisted to the configured path unless config path is empty. Sections starting with `:` are treated as on-the-fly backends and are not saved. Save defaults new files to `0600` but preserves existing permissions. Temporary files are cleaned up by defers.

Dependencies and integration points: depends on `config.GetConfigPath`, `config.Decrypt`, `config.Encrypt`, `goconfig`, `file.MkdirAll`, and platform `attemptCopyGroup`. It satisfies `config.Storage`.

Risks: reload detection uses modtime/size and may miss rare same-size same-modtime changes. Atomic replacement behavior depends on filesystem rename semantics. Errors during rename can leave backup temp files intentionally preserved. On-the-fly backend sections are silently not saved beyond a log.

Test signals: `configfile_test.go` covers read/write operations, reload, missing/no-config behavior, save permissions, symlink targets, and piped config decryption behavior.
