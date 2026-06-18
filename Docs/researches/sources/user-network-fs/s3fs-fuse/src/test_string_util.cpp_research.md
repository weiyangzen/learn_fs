# sources/user-network-fs/s3fs-fuse/src/test_string_util.cpp

## Purpose
Unit test driver for the string utility layer, including trimming, base64, numeric conversion, WTF8, CR encoding, sensitive-data masking, and xattr metadata parsing.

## Important APIs, Types, And Control Flow
Defines minimal globals expected by logging. `test_trim` checks left/right/full trim and quote peeling. `test_base64` validates empty and 1/2/3/4-byte base64 round trips. `test_strtoofft` checks decimal, invalid input, and hex conversions. `test_wtf8_encoding` compares ASCII, valid UTF-8, CP1252-like bytes, broken UTF-8, and mixed strings. `test_cr_encoding` round-trips CR, percent, CRLF, and mixed sequences. Masking tests verify AWS SigV4/SigV2 authorization, x-amz sensitive headers, proxy URLs, and client-cert password redaction. `test_parse_xattrs` checks build/parse for one, multiple, and colon-containing keys.

## State And Persistence
All state is local except construction of `S3fsLog` in `main`. No files or external services are touched.

## Dependencies And Integration Points
Includes `s3fs_logger.h`, `string_util.h`, `test_util.h`, and `types.h`. It is the main regression signal for utility functions that feed request signing, XML name handling, logging, and xattrs.

## Risks And Test Signals
The test leaves gaps for invalid base64, malformed URL escapes, malformed xattr JSON, invalid ISO8601, overflow in option duration parsing, and signed-char case conversion. It strongly signals intended round-trip behavior for WTF8 and CR encoding and intended redaction strings for logs.
