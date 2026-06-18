# sources/user-network-fs/libsmb2/lib/smb2-data-file-info.c

## Purpose
Provides structured encoders and decoders for SMB2 file information classes used by QUERY_INFO and SET_INFO.

## Important APIs, Types, And Functions
Functions include `smb2_decode_file_basic_info`, `smb2_encode_file_basic_info`, `smb2_decode_file_standard_info`, `smb2_encode_file_standard_info`, `smb2_decode_file_stream_info`, `smb2_encode_file_stream_info`, `smb2_decode_file_position_info`, `smb2_encode_file_position_info`, `smb2_decode_file_all_info`, `smb2_encode_file_all_info`, `smb2_decode_file_network_open_info`, `smb2_encode_file_network_open_info`, `smb2_decode_file_normalized_name_info`, and `smb2_encode_file_normalized_name_info`.

## Control Flow
The codecs translate between little-endian wire fields in `struct smb2_iovec` and libsmb2 C structs. Timestamp fields are converted between Windows filetime and `smb2_timeval`; `smb2_tv_timeval_to_win` preserves SMB sentinel values for "do not change" and "maximum". Variable names and stream names are converted between UTF-16 and UTF-8 and allocated under a caller-provided memory context. Stream info walks a next-entry chain and emits padded chained records.

## State And Persistence
Decoded strings are allocated with `smb2_alloc_data` under the provided memory context, usually a larger decoded object. Encode paths may mutate length fields such as `stream_name_length` and `file_name_length` to byte counts. No global state is used.

## Dependencies And Integration Points
These helpers are called directly by QUERY_INFO reply processing and SET_INFO request encoding. They rely on endian-safe `smb2_get_*`/`smb2_set_*`, time conversion, padding macros, and UTF helpers.

## Risks
Some encoders copy variable names without independently proving the destination iovec has room beyond the fixed header. `smb2_encode_file_stream_info` multiplies `stream_name_length` in place, which can surprise callers that reuse the struct. There are stray `#include <stdio.h>` lines in the middle of the file. Truncated decode behavior may hide malformed server replies by clipping names.

## Test Signals
Use round-trip tests for all supported classes, sentinel timestamp values, long and truncated names, multiple stream entries, UTF-16 conversion failures, short iovecs, and caller struct reuse after encoding.
