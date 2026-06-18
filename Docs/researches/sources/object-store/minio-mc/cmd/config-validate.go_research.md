# sources/object-store/minio-mc/cmd/config-validate.go

Purpose: Validates loaded v10 configuration before use or reporting.

Important APIs/types/functions: `validateConfigVersion`, `validateConfigFile`, and `validateConfigHost`.

Control flow: Version validation compares `config.Version` to `globalMCConfigVersion`. File validation accumulates errors from the version and every alias. Host validation checks API signature and host URL through config utility helpers, returning all host-level messages.

State and persistence: Stateless. Reads only the provided `configV10` value.

Dependencies/integration: Uses `errInvalidAPISignature`, `errInvalidURL`, `isValidAPI`, and `isValidHostURL`. Integrates with config load/init paths elsewhere.

Risks: Does not validate access/secret key length, alias names, path mode, session token, license, or API key fields. It also assumes `config` is non-nil.

Test signals: No direct tests in this subset; utility validator tests cover some leaf behavior.
