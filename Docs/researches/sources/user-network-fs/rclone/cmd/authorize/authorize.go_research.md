# sources/user-network-fs/rclone/cmd/authorize/authorize.go

Purpose: implements `rclone authorize`, the command used to authorize remotes for headless/config workflows. It registers flags to suppress browser opening and to select a custom HTML template, then delegates actual OAuth/config authorization to `config.Authorize`.

Control flow is simple: `init` registers command and flags; `RunE` checks for 1-3 args and calls `config.Authorize(context.Background(), args, noAutoBrowser, template)`. State changes happen inside config authorization, usually local token/config output or browser/listener flows. Dependencies are Cobra, rclone config, and command flag helpers. Risks include global flag variables, template path handling delegated elsewhere, and provider-specific authorization complexity outside this file. Tests check usage/help text formatting only.
