# sources/object-store/openstack-swift/swift/cli/config.py

Purpose: prints Swift server configuration in a flattened, operator-readable form. It can inspect normal config files or paste.deploy WSGI pipeline configs.

Important APIs: module-level `parser`, `_context_name()`, `inspect_app_config()`, and `main()`. `inspect_app_config()` extracts a paste context, filters, app context, and reconstructed pipeline string.

Control flow: `main()` parses server or config path arguments. Each argument is either an existing file or a server name resolved through `Server(arg).conf_files()`. For each config, it prints the file path, loads either `appconfig()` or `readconf()`, filters by section when requested, prints dict sections as INI sections, and prints scalar values as commented lines.

State and persistence: read-only; no config mutation.

Dependencies and integration: uses Swift `Server` manager discovery, `readconf`, and `appconfig`. It is a support tool for deployed operators checking effective config.

Risks: values are printed verbatim, so secrets in configs can be exposed to terminal logs. Section filtering is exact. Paste inspection assumes pipeline object context shape. Tests should cover file-vs-server lookup, WSGI pipelines, scalar config values, section filtering, and missing-argument error return.
