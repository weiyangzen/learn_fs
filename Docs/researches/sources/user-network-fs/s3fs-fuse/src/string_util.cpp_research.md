# sources/user-network-fs/s3fs-fuse/src/string_util.cpp

## Purpose
Implements the string, date, encoding, masking, and xattr serialization helpers declared in `string_util.h`. These routines sit on hot integration paths for S3 request signing, HTTP header construction/logging, object-key encoding, XML-safe object listing, and metadata-backed extended attributes.

## Important APIs, Types, And Control Flow
`str(timespec)` formats timestamps and recognizes `UTIME_OMIT`/`UTIME_NOW`. `s3fs_strptime`, `s3fs_strtoofft`, and `cvt_strtoofft` wrap portable parsing with explicit failure behavior. `trim_*`, `lower`, `upper`, and `peeloff` are pass-by-value transformations. URL encoding is centralized in `rawUrlEncode`, with general, path, and query variants differing only by allowed character sets. Date helpers emit RFC850, `YYYYMMDD`, and SigV3/SigV4-style ISO8601 strings and parse ISO8601 into GMT `time_t`. Binary helpers produce lower/upper hex, base64, and base64 decode output. WTF8 helpers detect invalid UTF-8 and map bad bytes into the Unicode private range, then reverse that mapping. CR helpers encode `%` and carriage returns before libxml2 parsing. Masking helpers redact sensitive request headers and option arguments. `parse_xattrs` and `raw_build_xattrs` transform the URL-encoded JSON-ish xattr header into `xattrs_t`.

## State And Persistence
The file is mostly stateless. It reads current time and locale, uses process `errno`, logs parse failures through `s3fs_logger`, and returns serialized strings for persistence in S3 metadata. `parse_xattrs` mutates the output map by clearing and rebuilding it.

## Dependencies And Integration Points
Depends on libc time/string conversion, `<regex>`, `fcntl.h`/`sys/stat.h` constants, `s3fs_logger.h`, `types.h`, and the header contract. Integration points include S3 auth dates, URL/object key handling, list-response XML preprocessing, logging redaction, command-line option logging, and xattr metadata.

## Risks And Test Signals
Risks include non-validating URL/base64 decoders accepting malformed bytes, `lower`/`upper` passing signed `char` to ctype functions, xattr parsing as ad hoc JSON split on commas/colons, `timegm` portability, `s3fs_strptime` returning `s + tellg()` where `tellg()` can be streampos-sensitive, and sensitive-header patterns missing new credentials. `test_string_util.cpp` covers trim/peeloff, base64 round trips, off_t conversion, WTF8, CR encoding, redaction, and xattr serialization; integration tests cover CR filenames, xattrs, external metadata, object keys, and logging behavior indirectly.
