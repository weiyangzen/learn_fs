# sources/user-network-fs/samba/source4/torture/ndr/ntprinting.c

## Purpose

`ntprinting.c` is a Samba torture-suite fixture for validating NDR unmarshalling of the generated `ntprinting_printer` type. It embeds captured printer metadata blobs and checks that Samba decodes classic NT printing state, `DEVMODE` fields, private driver data, registry-like printer data entries, and DOS-codepage-sensitive strings.

## Important APIs, Types, and Functions

- Includes `torture/ndr/ndr.h`, `librpc/gen_ndr/ndr_ntprinting.h`, `torture/ndr/proto.h`, and `param/param.h`.
- `ntprinting_printer_data` is the main captured binary fixture for a Kyocera printer.
- `ntprinting_printer_data_latin1` is a second fixture aimed at non-ASCII printer metadata and codepage handling.
- `ntprinting_printer_check()` validates the decoded `struct ntprinting_printer`, especially `info`, `devmode`, `nt_dev_private`, `count`, and `printer_data[]`.
- `ntprinting_printer_latin1_check()` manually builds a `DATA_BLOB`, sets `dos charset` to `CP1252`, calls `reload_charcnv()`, and invokes `ndr_pull_struct_blob()` with `ndr_pull_ntprinting_printer`.
- `ndr_ntprinting_suite()` registers a simple Latin-1 conversion test and a generated pull test through `torture_suite_add_simple_test()` and `torture_suite_add_ndr_pull_test()`.

## Control Flow

The suite constructor creates the `ntprinting` suite, registers the explicit Latin-1 path first, then registers the normal NDR pull fixture. The normal fixture is handled by the torture NDR framework, which pulls `ntprinting_printer_data` using generated NDR code and calls `ntprinting_printer_check()`. The Latin-1 path is not a generated-test macro wrapper: it mutates loadparm character conversion state, prepares `r.info.string_flags = LIBNDR_FLAG_STR_ASCII`, pulls the blob, and asserts selected decoded strings.

`ntprinting_printer_check()` is assertion-heavy and mostly linear. It checks scalar printer info, server/printer/share/port/driver strings, `DEVMODE` dimensions and flags, the private driver data length, then all 11 `printer_data` entries by pointer marker, registry-style name, type, and data length.

## State and Persistence Behavior

The file has no persistent storage and performs no network or filesystem I/O. Runtime state is limited to static byte arrays, decoded structures allocated by the torture framework, and a temporary loadparm character-conversion configuration change in `ntprinting_printer_latin1_check()`. That function does not restore the previous charset before returning, so it relies on test-suite isolation or later tests being robust to the modified `lp_ctx`.

## Dependencies and Integration Points

The test depends on Samba generated NDR for `ntprinting`, the torture assertion framework, TALLOC/DATA_BLOB helpers, and loadparm character conversion helpers. It integrates into the broader NDR torture registry through `ndr_ntprinting_suite()`, whose name is used by the test runner. The fixture is tightly coupled to generated parser semantics for ASCII strings, embedded private driver blobs, and `DEVMODE` layout.

## Risks and Edge Cases

- The Latin-1 check mutates global-ish configuration on `tctx->lp_ctx`; missing restoration can make failures order-dependent if another test reuses the context.
- The main fixture validates many decoded fields but does not fully inspect raw private driver data contents, only its length.
- A disabled pull-validate test documents that pull-push validation was not working at the time, so round-trip encoding is not covered.
- Hard-coded captured data can become stale if IDL definitions intentionally change; failures will need triage between parser regression and fixture drift.

## Test Signals

Strong signals include exact scalar/string assertions, 11 printer-data entry checks, private-driver length validation, and a targeted codepage conversion test. Weaker signals are the disabled pull-validate path and partial inspection of opaque private driver data. A relevant validation command would be the Samba NDR torture suite filtered to `ntprinting`.
