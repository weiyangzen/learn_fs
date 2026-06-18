# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_main.go

Purpose: This is the main program for `gocryptfs-xray`, a diagnostic tool for inspecting gocryptfs config files, encrypted names, master keys, and path mappings.

Important APIs and functions: It parses flags, loads config files, decrypts master keys when credentials are supplied, prints config/feature information, decodes encrypted filenames, and delegates control-socket path conversion.

Control flow and state: Depending on flags, it performs read-only config inspection, key derivation/decryption, or socket queries. It does not mount filesystems.

Dependencies and integration points: Integrates configfile, password reading, name/content crypto helpers, ctlsock, and fixture tests under `xray_tests`.

Risks and test signals: It can expose sensitive master-key/config information, so output handling matters. Signals include tests over AES-GCM and AES-SIV fixture filesystems and expected decode results.
