# sources/object-store/openstack-swift/swift/common/middleware/listing_formats.py

Purpose: Normalizes Swift account and container listings so clients can request `text/plain`, JSON, or XML while downstream Swift apps are forced to return JSON for conversion.

Important APIs and control flow: `get_listing_content_type` honors `format=` and `Accept`, raising `HTTPBadRequest` for invalid Accept parsing and `HTTPNotAcceptable` when no supported type matches. `account_to_xml`, `container_to_xml`, and `listing_to_text` convert JSON listing records. `ListingFilter.__call__` only handles valid account/container `GET` and `HEAD` requests, injects `format=json`, sets `swift.format_listing`, calls the downstream app, and only rewrites successful JSON responses below `MAX_CONTAINER_LISTING_CONTENT_LENGTH`. It adds `Vary: Accept` when negotiation was by Accept header, rewrites HEAD content metadata without consuming the body, filters reserved names unless `req.allow_reserved_names`, and returns 204 when the converted body is empty.

State, dependencies, and integration: No persistent state. It depends on swob requests, `HeaderKeyDict`, `valid_api_version`, `RESERVED`, and downstream JSON listing contracts.

Risks and test signals: Conversion mutates listing dictionaries with `pop`, so tests should pass fresh structures. Staticweb or non-JSON responses are intentionally passed through. Cover Accept negotiation, bad JSON fallback, large content-length fallback, reserved-name warnings, XML shape for account/container records, HEAD behavior, and empty-list 204 handling.
