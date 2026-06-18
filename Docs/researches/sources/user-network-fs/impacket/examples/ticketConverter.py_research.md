# sources/user-network-fs/impacket/examples/ticketConverter.py

## Purpose

`ticketConverter.py` converts Kerberos tickets between KRB-CRED `.kirbi` format and MIT/Heimdal ccache format. It can also decode a base64-wrapped input ticket before conversion.

## Important APIs, Types, and Functions

`parse_args()` defines input, output, and `--base64`. `main()` selects input source, detects format, dispatches conversion, and cleans temporary files. `is_kirbi_file()` checks for leading byte `0x76`. `is_ccache_file()` checks for leading byte `0x05`. `convert_kirbi_to_ccache()` uses `CCache.loadKirbiFile()` and `saveFile()`. `convert_ccache_to_kirbi()` uses `CCache.loadFile()` and `saveKirbiFile()`. `base64_decode_with_unwrap()` strips line wrapping and decodes Latin-1 text.

## Control Flow

The CLI prints the banner, parses arguments, optionally writes decoded base64 bytes to a named temporary file, then tests the effective input filename. Kirbi input is converted to ccache; ccache input is converted to kirbi; unknown leading bytes print an error. Base64 temporary files are closed and unlinked manually, with `PermissionError` handled for Windows.

## State and Persistence Behavior

The requested output file is written or overwritten by the `CCache` helper. With `--base64`, a temporary decoded ticket file is created with `delete=False` and then manually removed. No remote state is involved.

## Dependencies and Integration Points

It depends on `impacket.krb5.ccache.CCache`, `base64`, `struct`, `tempfile`, and filesystem access. It integrates with tools that use kirbi/KRB-CRED exports and ccache files consumed by Impacket/Kerberos workflows.

## Risks and Edge Cases

`decoded_file` is only defined when `--base64` is set; later guarded use is safe but fragile if code is rearranged. Format detection reads only one byte and can raise on empty files. Unknown formats do not set a nonzero exit status. Base64 decoding reads the whole file into memory and leaves temp files behind on non-`PermissionError` cleanup failures or crashes.

## Test Signals

Tests should cover kirbi-to-ccache conversion, ccache-to-kirbi conversion, base64 unwrap/cleanup, unknown and empty files, output overwrite behavior, and cleanup failure handling. Fixture tickets can be minimal parser-compatible files or mocked `CCache` calls.
