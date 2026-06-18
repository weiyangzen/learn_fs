# sources/object-store/openstack-swift/swift/proxy/controllers/info.py

## Purpose
This module implements the proxy `/info` controller, which returns public Swift capability/configuration data and optional admin-only sections when a valid HMAC-signed request is supplied.

## Important APIs, Types, and Functions
`InfoController` extends `Controller` with `server_type = 'Info'`. It exposes public `GET()`, `HEAD()`, and `OPTIONS()` methods decorated with `delay_denial`. `GETorHEAD()` performs the actual authorization and response generation. Constructor parameters include `expose_info`, `disallowed_sections`, and `admin_key`.

## Control Flow
GET and HEAD delegate to `GETorHEAD()`. OPTIONS returns an immediate 200 with `Allow: HEAD, GET, OPTIONS`. `GETorHEAD()` rejects all requests with 403 when info exposure is disabled. If either `swiftinfo_sig` or `swiftinfo_expires` is present, the request becomes an admin request: an admin key must exist, expiry must parse as an integer and be in the future, and the signature must match a constant-time comparison against HMACs for allowed methods (`GET` for GET, `HEAD` or `GET` for HEAD). Valid admin requests call `get_swift_info(admin=True, ...)`; normal requests call it with `admin=False`. CORS response headers are echoed when an Origin is present.

## State and Persistence Behavior
The controller is stateless per request. It reads registry data from `get_swift_info()` and serializes it as ASCII JSON. No cache or persistent data is written.

## Dependencies and Integration Points
It depends on Swift's registry of capability info, HMAC helper, constant-time string comparison, and swob response classes. Its delay-denial decorators allow auth middleware to run after request context is prepared, matching other public controller methods.

## Risks and Edge Cases
Admin access depends entirely on secrecy of `admin_key`, expiry validation, and constant-time signature comparison. HEAD accepts signatures generated for either HEAD or GET, which is intentional compatibility behavior. If either signature or expiry is partially supplied, the request is treated as admin and may return 401/403 rather than public info. CORS is permissive for `/info`, echoing the Origin and exposing only `x-trans-id`.

## Test Signals
Tests should cover disabled exposure, public GET/HEAD, OPTIONS allow header, valid and expired admin signatures, missing admin key, invalid expiry, invalid signature, HEAD signed as GET, disallowed section filtering, and CORS headers.
