## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.cc

Purpose: implements parsers for HTTP digest headers, Content-Length, and Transfer-Encoding. These helpers centralize security-sensitive header interpretation for the HTTP protocol.

Important APIs and control flow: `parseReprDigest()` splits comma-separated entries, expects `<name>=:<base64>:`, trims the name/value, base64-decodes the digest to hex bytes via `base64DecodeHex()`, lowercases the digest name, and stores it in an output map while ignoring malformed entries. `parseWantReprDigest()` parses comma-separated `<name>=<uint8>` preferences, lowercases names, clamps preferences to 10, and discards invalid values. `parseContentLength()` strips trailing CRLF/OWS, rejects empty, non-digit, signed, embedded-whitespace, and overflow values, returning distinct negative error codes. `parseTransferEncoding()` splits tokens, trims/lowercases them, requires whole-token `chunked`, and requires it to be the final non-empty token.

State and persistence: all functions are stateless and write only caller-supplied maps or return codes.

Dependencies and integration: used by `XrdHttpProtocol`/request parsing to populate request digest maps and validate message framing. It relies on `XrdOucTUtils`, `XrdOucUtils`, and `XrdHttpUtils::base64DecodeHex`.

Risks and test signals: Content-Length and Transfer-Encoding parsing are request-smuggling defenses and need exhaustive malformed-input tests. Repr-Digest silently ignores malformed data, so callers must decide whether leniency is acceptable. Tests should cover whitespace, case, duplicate keys, invalid base64, overflow, plus/minus signs, multiple TE codings, `chunked` substrings, and chunked-not-last.
