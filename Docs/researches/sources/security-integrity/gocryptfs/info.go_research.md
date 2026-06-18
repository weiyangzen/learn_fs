# sources/security-integrity/gocryptfs/info.go

Purpose: This file implements the `-info` operation, pretty-printing a gocryptfs config file for humans while hiding sensitive fields.

Important APIs and functions: `info(filename)` loads the config, strips or redacts encrypted key material and sensitive FIDO2 values, marshals remaining metadata, and prints it.

Control flow and state: It reads a config file, transforms an in-memory representation, and writes output. It does not modify the config on disk.

Dependencies and integration points: Uses `internal/configfile`, JSON formatting, logging, and CLI operation dispatch.

Risks and test signals: Sensitive fields must remain redacted. Signals include `-info` output containing version/feature flags but not raw encrypted key or secret token material.
