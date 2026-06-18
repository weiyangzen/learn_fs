# sources/distributed-fs/xrootd/src/XrdMacaroons/CMakeLists.txt

Purpose: Configures build/install of the Macaroons authorization and HTTP extension plugin.

Important APIs/types/functions: Requires `ENABLE_MACAROONS`, HTTP support when force-enabled, `Macaroons`, `json-c` on non-Apple, and `BUILD_HTTP`. Builds module `XrdMacaroons-${PLUGIN_VERSION}` from plugin entry, authz, configure, and handler sources. Links `XrdHttpUtils`, `XrdUtils`, `XrdServer`, `uuid`, OpenSSL crypto, Macaroons, JSON, and dl, with an ELF version script on non-Apple.

Control flow: Missing feature flags or dependencies return without building unless force-enabled paths require hard errors.

State and persistence: Build metadata only.

Dependencies and integration points: Produces both authorization plugin symbols and HTTP extension handler symbols for macaroon issuance/validation.

Risks: `JSON_FOUND` is referenced even on Apple where pkg-config block is skipped; parent CMake may define it, but platform behavior should be checked. Macaroons requires HTTP build support.

Test signals: Configure with enabled/disabled macaroons, missing libmacaroons/json-c, force-enabled HTTP absence, non-Apple version-script link, and plugin load.
