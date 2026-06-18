# sources/user-network-fs/cifs-utils/smb2-quota

## Purpose
`smb2-quota` is a Python 3 command-line tool that queries quota information for a file on a Linux CIFS/SMB mount using the CIFS query-info ioctl.

## Important APIs, types, and functions
The script uses `fcntl.ioctl` with `CIFS_QUERY_INFO = 0xc018cf07`, an `array.array('B')` buffer, and `struct.pack_into`/`unpack_from` to marshal the quota request and response. `SID` decodes Windows SIDs. `QuotaEntry` decodes one quota record, formats used/threshold/limit fields, computes percentage and status, and prints tabular, CSV, or list output. `Quota` walks the variable-length quota entry chain through each entry's next-offset field. `parser_check` builds and submits the ioctl request.

## Control flow
`main` parses `--tabular`, `--csv`, `--list`, and a required filename. Tabular is the default when no format is chosen. Each selected format calls `parser_check`, which opens the file read-only, initializes a 16 KiB query buffer with quota info type and lengths, performs the ioctl, slices the returned payload, constructs `Quota`, and prints it.

## State and persistence behavior
The tool is read-only. It does not cache or persist data locally; all state comes from the mounted share via the kernel CIFS client and server quota support.

## Dependencies and integration points
It depends on Python 3 stdlib modules and Linux CIFS ioctl ABI support. It integrates with cifs.ko and a mounted SMB share path. Output is intended for humans or scripts, with CSV mode providing a stable simple form.

## Risks
The parser assumes a fixed 16 KiB buffer and does not retry on larger quota responses. `percent_used` divides by `limit` unless limit equals threshold; unlimited quota values can produce misleading percentages. It catches ioctl errors but does not exit nonzero explicitly. The request setup packs two adjacent one-byte fields both commented as "return single"; that warrants checking against the kernel ABI.

## Test signals
Unit-test SID decoding and chained quota parsing with synthetic buffers. On an SMB server with quotas enabled, test all output modes, unlimited and no-warning values, multiple entries, ioctl failures on non-CIFS files, and behavior when response size approaches the fixed buffer limit.
