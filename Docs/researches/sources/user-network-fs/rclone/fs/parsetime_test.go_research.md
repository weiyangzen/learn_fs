# Research: sources/user-network-fs/rclone/fs/parsetime_test.go

## sources/user-network-fs/rclone/fs/parsetime_test.go

Purpose: tests `Time` parsing, formatting, scanner, JSON unmarshal, and JSON marshal behavior. It also asserts flag interfaces.

Control flow temporarily replaces `timeNowFunc` with a fixed instant, then runs table cases for empty/error input, relative units, bare numeric seconds, negative offsets, `"off"`, absolute local and RFC3339 dates, scanner reads, JSON string values, non-string JSON errors, and marshal output. State is the global time callback restored with defer. Dependencies include `encoding/json`, `fmt.Sscan`, and testify. Integration signal is strong for config/flag behavior where users specify cutoff times as either absolute timestamps or ages. Risks covered include erroring on non-string JSON, zero time semantics, local-vs-UTC dates, and future timestamps from negative relative inputs. A small gap is concurrency safety around the global test override, which relies on non-parallel tests.
