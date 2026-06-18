# sources/test-tools/syzkaller/prog/checksum.go

Purpose: derives runtime checksum calculation descriptors for syscall arguments, including Internet checksums and IPv4/IPv6 pseudo-header checksums.

Important APIs/types/functions: `CsumChunkKind`, `CsumInfo`, and `CsumChunk` model checksum inputs. `calcChecksumsCall` is the main entry point. `findCsummedArg`, `composePseudoCsumIPv4`, `composePseudoCsumIPv6`, `extractHeaderParams`, and `getFieldByName` locate checksum-covered regions and construct chunk lists.

Control flow and state: `calcChecksumsCall` first collects checksum fields with `ForeachArg`, builds a child-to-parent map for structs, and returns nil maps when no checksum is present. Inet checksums reference the configured parent or named ancestor. Pseudo checksums scan for IPv4/IPv6 header structs, extract `src_ip`/`dst_ip`, add protocol and packet length constants in network byte order, and record all args used by checksum instructions.

Dependencies and integration: used by `encodingexec.go` before copyin/checksum emission. Depends on `CsumType`, `CsumKind`, struct template names, swap helpers, and traversal from `analysis.go`.

Risks: missing headers, missing parent fields, bad `src_ip`/`dst_ip` sizes, and unknown checksum kinds panic. Named-buffer lookup currently compares type names and has a TODO for template argument names.

Test signals: `checksum_test.go` randomly generates and mutates programs, calling exported `CalcChecksumsCall` on every call. `encodingexec_test.go` includes exact executor-byte expectations for nested IPv4/TCP checksum instructions.
