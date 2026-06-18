# File Research: sources/virtualization/spdk/module/keyring/linux/keyring_rpc.c

Adds startup JSON-RPC control for Linux keyring backend options.

Key elements:
- Registers `keyring_linux_set_options`.
- Decodes optional `enable`.
- Seeds RPC request from current options.
- Calls `keyring_linux_set_opts()` and returns boolean success.

Dependencies:
- `keyring_linux.h`, SPDK JSON-RPC, string/util helpers, generated RPC context.

Research notes:
- Startup timing matters because backend initialization checks the enable option.
