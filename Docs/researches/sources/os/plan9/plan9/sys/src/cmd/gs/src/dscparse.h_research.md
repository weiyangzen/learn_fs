# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.h

Purpose: Public interface and data model for Ghostscript/Ghostgum DSC parsing. It defines the parser state, DSC comment return codes, page/media/bounding-box metadata, preview metadata, DCS 2.0 plate-file metadata, color separation metadata, and callback hooks.

Key structures and APIs:
- `CDSC`: central parser object containing public document metadata and private scan state.
- `CDSCPAGE`, `CDSCMEDIA`, `CDSCBBOX`, `CDSCFBBOX`, `CDSCCTM`: parsed page/media/geometry records.
- `CDSCDOSEPS`, `CDSCMACBIN`: binary EPS/MacBinary offsets.
- `CDSCSTRING`: chunk allocator list for parser-owned strings.
- `CDCS2`, `CDSCCOLOUR`: DCS 2.0 and process/custom color records.
- Public lifecycle and parsing calls: `dsc_init`, `dsc_init_with_alloc`, `dsc_free`, `dsc_new`, `dsc_ref`, `dsc_unref`, `dsc_set_length`, `dsc_scan_data`, `dsc_fixup`.
- Callback configuration: `dsc_set_error_function`, `dsc_set_debug_function`.
- Utility/exported helpers: `dsc_find_platefile`, `dsc_stricmp`, `dsc_add_page`, `dsc_add_media`, `dsc_set_page_bbox`, `dsc_display`.

Implementation notes:
- Offsets use configurable `DSC_OFFSET`, defaulting to `unsigned long`; large-file support requires overriding this typedef/macro pair.
- Line handling is bounded around DSC’s 255-character legal line length, with a larger 8192-byte scan buffer.
- Return codes group comments by DSC section, with ranges for header, preview, defaults, prolog, setup, page, trailer, and EOF.
- `struct CDSC_s` contains `char dummy[1024]` before real fields, likely ABI padding or legacy compatibility.
- The header mixes public and private fields in one exposed struct, so consumers can couple to internal scan state.

Filesystem relevance: Indirect. It models document offsets and file lengths for PostScript/EPS parsing but has no OS/VFS behavior.
