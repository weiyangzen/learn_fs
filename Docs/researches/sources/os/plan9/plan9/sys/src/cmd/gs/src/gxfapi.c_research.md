# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.c

Implements UFST font callback dispatch support.

- Includes Ghostscript core headers and UFST headers:
  - `cgconfig.h`
  - `port.h`
  - `shareinc.h`
- Provides stub callbacks returning `NULL`:
  - `stub_PCLEO_charptr`
  - `stub_PCLchId2ptr`
  - `stub_PCLglyphID2Ptr`
- Maintains three static function pointers initially pointing to stubs:
  - `m_PCLEO_charptr`
  - `m_PCLchId2ptr`
  - `m_PCLglyphID2Ptr`
- Exports callback functions called by UFST:
  - `PCLEO_charptr`
  - `PCLchId2ptr`
  - `PCLglyphID2Ptr`
- `gx_set_UFST_Callbacks` installs client-provided callback functions.
- `gx_reset_UFST_Callbacks` restores stubs.

Important limitation: comments state these callback variables are static until graphics-library reentrancy and UFST callback reentrancy are fixed, so this dispatch mechanism is not reentrant/thread-local.
