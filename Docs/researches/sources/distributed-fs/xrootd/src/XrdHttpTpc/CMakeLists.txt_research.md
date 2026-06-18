# sources/distributed-fs/xrootd/src/XrdHttpTpc/CMakeLists.txt

Purpose: Configures build/install of the HTTP third-party-copy plugin.

Important APIs/types/functions: Requires `ENABLE_HTTP`, finds CURL, sets `BUILD_TPC`, builds module `XrdHttpTPC-${PLUGIN_VERSION}` from configure, multistream, PMark, state, stream, handler, and utility sources, links XRootD server/utils/http utils, `CURL::libcurl`, OpenSSL, pthreads, and dl, and applies an ELF version script on non-Apple platforms.

Control flow: If HTTP is disabled or CURL is unavailable, returns without building. With `FORCE_ENABLED`, CURL is required and configure failure is hard.

State and persistence: Build metadata only.

Dependencies and integration points: Produces the `XrdHttpGetExtHandler` module used by XrdHTTP to handle `COPY` and `OPTIONS`.

Risks: Plugin availability is conditional on CURL and HTTP. Link dependency list must stay in sync with added OpenSSL/XRootD subsystem usage. Version-script handling is platform-specific.

Test signals: Configure with and without CURL, with `FORCE_ENABLED`, on non-Apple and Apple platforms, and load the installed TPC module.
