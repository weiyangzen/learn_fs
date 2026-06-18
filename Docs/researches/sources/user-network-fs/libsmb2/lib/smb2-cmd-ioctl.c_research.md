<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-ioctl.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-ioctl.c

## Purpose

`smb2-cmd-ioctl.c` implements SMB2 IOCTL request and reply marshalling. It supports validate-negotiate-info locally, reparse point decoding on replies, and passthrough mode for control codes the library does not understand.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_ioctl_async`, `smb2_cmd_ioctl_reply_async`, `smb2_process_ioctl_fixed`, `smb2_process_ioctl_variable`, `smb2_process_ioctl_request_fixed`, and `smb2_process_ioctl_request_variable`. Important structures include `smb2_ioctl_request`, `smb2_ioctl_reply`, `smb2_ioctl_validate_negotiate_info`, and `smb2_reparse_data_buffer`.

## Control Flow

Request encoding fills control code, file ID, input offset/count, max response sizes, flags, and appends raw input. Reply encoding writes fixed fields and either transcodes `SMB2_FSCTL_VALIDATE_NEGOTIATE_INFO` or copies output in passthrough mode. Fixed reply parsing validates offsets, reads input/output metadata, and returns enough bytes to include padding, input, and output. Variable parsing decodes reparse data for `GET_REPARSE_POINT` or copies raw output. Server-side request variable parsing decodes validate-negotiate info or exposes raw input in passthrough mode.

## State And Persistence Behavior

State is transient in request/reply payloads and context-allocated output buffers. IOCTL operations can query or mutate remote filesystem/device state depending on the control code; this module itself does not persist anything.

## Dependencies And Integration Points

It depends on core PDU helpers, `smb2_decode_reparse_data_buffer`, passthrough mode on `smb2_context`, and negotiate/security state for validate-negotiate use. It is used by higher-level symlink/reparse and SMB3 validation paths.

## Risks And Edge Cases

Reply encoding allocates `PAD_TO_64BIT(len)` bytes but zeroes `rep->output_count` bytes, which can exceed the allocated length if `len` is reduced for a transcoded output. Raw output copying in `smb2_process_ioctl_variable` copies `iov->len - IOV_OFFSET_IOCTL`, not strictly `output_count`, into a buffer sized `output_count`. Unsupported control codes fail unless passthrough is enabled. Offset validation checks lower bounds but relies on the receive layer and later length checks for upper bounds.

## Test Signals

Test validate-negotiate request/reply encoding, reparse point decoding, passthrough raw input/output, unsupported code errors, offset overlap and overrun rejection, output-count versus padding behavior, and integration with SMB3 negotiate validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-ioctl.c -->
