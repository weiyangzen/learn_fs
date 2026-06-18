# sources/user-network-fs/s3fs-fuse/src/string_util.h

## Purpose
Declares the common string utility interface used across s3fs-fuse for URL/path encoding, HTTP/date formatting, binary encodings, WTF8 conversion, redaction, and S3 metadata xattr parsing.

## Important APIs, Types, And Control Flow
The header exports `SPACES`, `CaseInsensitiveStringView`, `is_prefix`, `SAFESTRPTR`, and `WTF8_ENCODE`. Public functions include timestamp formatting/parsing, off_t conversion, trim/case/quote helpers, RFC850/SigV3/SigV4 date construction, URL encode/decode variants, keyword extraction, hex/base64 encode/decode, WTF8 encode/decode, CR encode/decode, sensitive-string/header/argument masking, and `parse_xattrs`/`raw_build_xattrs`.

## State And Persistence
It has no runtime state except references held by `CaseInsensitiveStringView`. `WTF8_ENCODE` creates a local buffer and pointer alias in the caller scope, so its state and lifetime are macro-local and must be used carefully.

## Dependencies And Integration Points
Includes `<cstring>`, `<ctime>`, `<string>`, `<strings.h>`, and `types.h`. It is integrated by network/auth, logging, option, metadata, and filesystem code that need consistent object-key, header, or metadata transformations.

## Risks And Test Signals
`CaseInsensitiveStringView` stores a raw `const char*`; constructing it from a temporary `std::string` leaves a dangling pointer. Macro expansion in `WTF8_ENCODE` requires an `_ARG` variable naming convention and can surprise scopes. Tests in `test_string_util.cpp` and helper assertions in `test_util.h` exercise the exported routines most directly.
