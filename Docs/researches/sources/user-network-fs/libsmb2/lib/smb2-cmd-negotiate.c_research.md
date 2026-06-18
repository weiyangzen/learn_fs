<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-negotiate.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-negotiate.c

## Purpose

`smb2-cmd-negotiate.c` implements SMB2 NEGOTIATE request and reply marshalling, including SMB3.1.1 negotiate contexts for preauth integrity and encryption capability.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_negotiate_async`, `smb2_cmd_negotiate_reply_async`, `smb2_process_negotiate_fixed`, `smb2_process_negotiate_variable`, `smb2_process_negotiate_request_fixed`, and `smb2_process_negotiate_request_variable`. Internal helpers encode/parse preauth, encryption, netname, and generic negotiate contexts.

## Control Flow

Request encoding writes fixed negotiate fields, dialect array, client GUID, security mode, capabilities, and, for SMB2 version any/any3/3.1.1, appends preauth SHA-512 and AES-128-CCM encryption contexts. Reply encoding writes server capabilities, sizes, times, security buffer metadata, and optional contexts. Fixed parsing reads security buffer and context offsets, validates overlap and PDU bounds, and returns variable length. Variable parsing attaches the security buffer and parses known SMB3.1.1 contexts.

## State And Persistence Behavior

State is transient in PDU payloads but negotiation establishes durable-in-context protocol state elsewhere: selected dialect, security mode, capabilities, cipher, server GUID, maximum sizes, and preauth hash inputs. The file reads `smb2->salt`, `version`, `dialect`, `spl`, and `passthrough`-adjacent context state but does not write persistent storage.

## Dependencies And Integration Points

It depends on libsmb2 constants, UTF-16 conversion for netname context parsing, SHA-512 advertised hash constants, encryption constants, and PDU/iovec helpers. It is the first SMB2 command in normal client connections and feeds session setup/signing/sealing decisions.

## Risks And Edge Cases

In reply encoding, `seclen` is initialized from `security_buffer_length` but then overwritten with `PAD_TO_64BIT(len)`, so allocation/copy size appears tied to fixed header length rather than security buffer length. Unknown negotiate contexts are fatal for replies and requests except for a few known ignored types, which may reduce forward compatibility. Request context parsing only interprets contexts when dialect list contains 3.1.1. Offset loops check `offset > iov->len` after reading type/length, so truncated context headers need careful receive-layer coverage.

## Test Signals

Test dialect arrays for SMB2.0.2 through SMB3.1.1, negotiate context alignment/counts, preauth salt encoding, encryption cipher parsing, security buffer bounds, unknown context behavior, server request parsing with and without 3.1.1 dialect, and full negotiate/session-setup integration against Samba and Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-negotiate.c -->
