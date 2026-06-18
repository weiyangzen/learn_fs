<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key_name.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/key_name.rs

Purpose: Enumerates all recognized policy condition key names across S3, AWS, JWT, LDAP, STS, and service-account namespaces, and maps between strings, short names, and policy variable placeholders.

Important APIs/types/functions: `KeyName` wraps `AwsKeyName`, `JwtKeyName`, `LdapKeyName`, `StsKeyName`, `SvcKeyName`, and `S3KeyName`. `TryFrom<&str>` dispatches by namespace prefix. `COMMON_KEYS` lists keys used for variable substitution in string conditions. `prefix`, `name`, and `var_name` compute prefix length, short key name, and `${...}` placeholder. Each namespace enum uses `strum` for exact string parsing/serialization.

Control flow: Parsing is case-sensitive and prefix-specific; unknown prefixes or misspelled keys return `InvalidKeyName`. `name()` returns the part after the namespace prefix by slicing the enum string. `var_name()` rebuilds a `${namespace:key}` string using the full enum string.

State/persistence behavior: No external state. These enum variants define the accepted persisted policy condition key vocabulary.

Dependencies/integration: Uses serde and `strum`. `Key`, `StringFunc` variable substitution, `Functions::references_key_name`, and condition validators depend on this vocabulary.

Risks/test signals: Adding a condition key requires updating the right enum and possibly `COMMON_KEYS` if it should participate in variable substitution. `KeyName::name()` returns short names that may collide across namespaces, so request context maps need consistent naming. Tests cover successful parsing/serde, failed case-sensitive parsing, and JWT roles support.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key_name.rs -->
