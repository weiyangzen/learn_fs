# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib.h

This public header defines the main RADIUS library constants and API. It declares packet codes for access request/accept/reject/challenge and accounting request/response, plus a large set of standard RADIUS attribute type constants and enumerated values for service type, framed protocol, compression, NAS port type, accounting status/authentication/termination causes, EAP, Message-Authenticator, IPv6 attributes, and related fields.

The API is centered on opaque `struct rad_handle`. It exposes handle creation for authentication and accounting (`rad_auth_open`, `rad_acct_open`, deprecated `rad_open`), server/config setup, close, request creation, attribute writers for address/int/string/raw data, Message-Authenticator insertion, request sending in blocking and staged forms, response attribute iteration, conversion helpers, request authenticator extraction, server secret lookup, error-string access, and generic password demangling.

The header includes only system types and IPv4 address definitions needed by callers. Microsoft/vendor-specific support is separated into `radlib_vs.h`, though private code includes it for implementation.
