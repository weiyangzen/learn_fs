# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.c

Implements ICCBased color space support.

Major responsibilities:
- Defines `icmFileGs`, an adapter from Ghostscript `stream` to the external `icclib` file interface.
- Provides GC/finalization logic for `gs_cie_icc`, including cleanup of foreign-memory ICC profile, lookup, and file objects.
- Defines the `CIEICC` color space type and methods: component count, alternate space, initial color, range restriction, concrete space selection, concretization, refcount adjustment, install, and serialization.
- Loads ICC profiles with `gx_load_icc_profile`.

Profile loading:
- Verifies stream identity with `file_id`.
- Creates `new_icc`, wraps the stream, reads the profile, validates profile class, PCS, and source color space/component count.
- Obtains an icclib lookup object using default intent.
- Stores profile illuminant as WhitePoint and records whether PCS is Lab.

Color conversion:
- If no profile is loaded, delegates to the alternate color space.
- Otherwise restricts input, handles Lab input scaling, performs ICC lookup, converts PCS Lab to XYZ when needed, and feeds CIE remapping.

Risks and quirks:
- ICC profile objects are allocated in foreign memory and cleaned in a finalizer.
- The stream pointer must be refreshed lazily before lookup because streams can relocate.
- Serialization reads the whole ICC stream into the output; some failures are marked `unregistered` as unimplemented.
