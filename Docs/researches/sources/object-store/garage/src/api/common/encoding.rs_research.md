## sources/object-store/garage/src/api/common/encoding.rs

Purpose: provides AWS-style URI percent encoding for canonical signatures and response/query handling.

Important APIs/types/functions: `uri_encode(string, encode_slash)`.

Control flow: iterates Unicode scalar values, leaves alphanumeric plus `_`, `-`, `~`, `.` untouched, optionally encodes `/` as `%2F`, and percent-encodes UTF-8 bytes of all other characters with uppercase hex.

State/persistence: none.

Dependencies/integration: used by SigV4 canonical request generation. Slash handling differs between canonical path and query string needs.

Risks: incorrect encoding breaks signature interoperability. The function works by `char` then UTF-8 bytes, so it assumes valid Rust `&str`; invalid path bytes must be handled before this layer.

Test signals: local tests cover URLs, spaces, non-ASCII characters, slash-preserving mode, and output growth beyond double input length.
