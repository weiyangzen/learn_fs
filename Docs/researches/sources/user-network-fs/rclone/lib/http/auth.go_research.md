# sources/user-network-fs/rclone/lib/http/auth.go

Source read signal: reviewed complete local file (135 lines, sha256 11431c0ded0b3155).

Purpose: Defines HTTP authentication help text, configuration, flags, and the custom-auth callback type.

Important APIs/types/functions: Exports `AuthHelp`, `CustomAuthFn`, `AuthConfigInfo`, `AuthConfig`, `AddFlagsPrefix`, `AddAuthFlagsPrefix`, and `DefaultAuthCfg`.

Control flow: `AuthHelp` templates prefix-aware documentation. `AddFlagsPrefix` binds htpasswd, realm, user, pass, salt, and user-from-header options. `DefaultAuthCfg` returns the default MD5 crypt salt.

State and persistence behavior: Config structs are in-memory; no auth data is persisted here. Password and htpasswd values are supplied by flags/config elsewhere.

Dependencies and integration points: Uses `html/template`, `pflag`, rclone `fs.Options`, and config flag helpers. `server.go` consumes `AuthConfig` to install middleware.

Risks and test signals: User-from-header is powerful and documented as proxy-trust-sensitive. The default salt must stay synchronized with `AuthConfigInfo`; tests only verify help template prefix substitution.
