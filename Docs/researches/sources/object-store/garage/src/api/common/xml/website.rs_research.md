## sources/object-store/garage/src/api/common/xml/website.rs

Purpose: serializes/deserializes and validates S3 static website XML configuration, then converts routing rules into Garage's website model.

Important APIs/types/functions: `WebsiteConfiguration`, `RoutingRules`, `RoutingRule`, `Key`, `Suffix`, `Target`, `Condition`, `Redirect`; validation methods on each; `WebsiteConfiguration::into_garage_website_config`; `RoutingRule::{from_garage_routing_rule, into_garage_routing_rule}`.

Control flow: validation forbids `RedirectAllRequestsTo` together with index/error/routing fields, validates non-empty error key, index suffix without slash, HTTP/HTTPS protocols, <=1000 routing rules, condition status code currently only 404, and redirect code constraints. Conversion currently rejects `RedirectAllRequestsTo` as not implemented and builds `WebsiteConfig` with default `index.html`, optional error doc, and routing rules with default 302 redirect code.

State/persistence: no direct persistence; produces `WebsiteConfig` stored in bucket state by callers.

Dependencies/integration: used by S3 website configuration handlers and admin domain checks. Depends on `garage_model::bucket_table` website/routing types.

Risks: `RedirectAllRequestsTo` is documented by XML shape but intentionally not implemented. The validation permits Netlify-like 200/404 rewrite semantics with restrictions. `Suffix::validate` uses bitwise `|` on booleans, which works but does not short-circuit.

Test signals: local tests cover deserialization/serialization of full and empty website configurations.
