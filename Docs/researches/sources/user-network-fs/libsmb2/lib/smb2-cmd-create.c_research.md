<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-create.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-create.c

## Purpose

`smb2-cmd-create.c` implements SMB2 CREATE open/create request and reply marshalling. It converts paths to SMB UTF-16 form, handles create contexts as opaque buffers, parses replies with file IDs and metadata, and supports server-side request decoding.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_create_async`, `smb2_cmd_create_reply_async`, `smb2_process_create_fixed`, `smb2_process_create_variable`, `smb2_process_create_request_fixed`, and `smb2_process_create_request_variable`. Internal helpers are request/reply encoders and offset macros `IOV_OFFSET_CREATE` and `IOVREQ_OFFSET_CREATE`.

## Control Flow

Request encoding fills desired access, attributes, share access, disposition, options, name offset/length, and create-context fields. Nonempty names are converted from UTF-8 to UTF-16 and `/` characters are rewritten to `\`. Empty names still add padding so contexts align. Reply encoding writes oplock/flags/action, timestamps, sizes, attributes, file ID, and optional context. Parsing first validates fixed size and offsets, returns the variable byte count, then variable parsing attaches context pointers or converts the request name back to allocated UTF-8.

## State And Persistence Behavior

State is transient in PDU payloads and buffers. Server-visible remote state includes opening or creating filesystem objects, acquiring oplocks/leases through create contexts, and returning durable file IDs. Request variable parsing allocates name memory through `smb2_alloc_init`, tying it to the context allocator.

## Dependencies And Integration Points

The file depends on UTF conversion helpers, iovec management, endian accessors, and create context definitions in libsmb2 headers. It is used by higher-level open, stat, directory, and create-path APIs.

## Risks And Edge Cases

Create contexts are opaque and not validated here. Offset arithmetic assumes sane received lengths; overlap checks exist, but variable parsers rely on the receive layer to have read the requested length. Request variable parsing decodes the name from the start of the variable iovec, which is correct only because the fixed parser requested padding up to `name_offset`. Empty-name padding and alignment are protocol-sensitive. Path conversion rewrites all slash codepoints, which may surprise callers expecting literal slash handling.

## Test Signals

Test UTF-8/UTF-16 conversion, slash rewriting, empty name with contexts, context alignment, offset overlap rejection, malformed lengths, reply file ID and metadata parsing, server-side name allocation lifetime, and full open/create integration against a test SMB server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-create.c -->
