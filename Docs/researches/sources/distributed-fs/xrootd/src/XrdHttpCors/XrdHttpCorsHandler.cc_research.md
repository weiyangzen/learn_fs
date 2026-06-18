# sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.cc

Purpose: Implements the default basic CORS plugin.

Important APIs/types/functions: `XrdHttpCorsGetHandler` returns a new `XrdHttpCorsHandler`. `Configure` gathers `cors.origin` directives with `XrdOucGatherConf`. `addAllowedOrigin` trims and stores origins in an unordered set. `getCORSAllowOriginHeader` returns `Access-Control-Allow-Origin: <origin>` for exact matches.

Control flow: Configuration gathers all `cors.origin` tokens from the config body, iterates tokens, and calls `addAllowedOrigin`. At request time the plugin performs exact string lookup against the set and returns either a formed header or `nullopt`.

State and persistence: Allowed origins live in `m_origins` for the plugin instance lifetime. No disk writes or dynamic refresh are present.

Dependencies and integration points: Depends on `XrdOucGatherConf`, `XrdOucUtils::trim`, `XrdVersion` plugin metadata, and the `XrdHttpCors` ABI.

Risks: Origin matching is exact and does not normalize scheme/host case or trailing slash beyond trimming whitespace. It does not generate other CORS headers such as methods, headers, or credentials. Multiple tokens are accepted without syntactic validation.

Test signals: Config with repeated and space-delimited `cors.origin`, whitespace trimming, exact mismatch behavior, empty token suppression, and plugin version symbol loading.
