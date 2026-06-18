## sources/object-store/garage/src/api/common/xml/cors.rs

Purpose: serializes/deserializes S3 CORS XML configuration and converts it to/from Garage bucket CORS model rules.

Important APIs/types/functions: `CorsConfiguration`, `CorsRule`, schema helper structs `AllowedMethod`, `AllowedHeader`, `ExposeHeader`, `CorsConfiguration::{validate, into_garage_cors_config}`, and `CorsRule::{validate, to_garage_cors_rule, from_garage_cors_rule}`.

Control flow: XML maps `CORSConfiguration`/`CORSRule` child elements into vectors of `Value`/`IntValue`. Validation parses allowed methods as HTTP methods and allowed/exposed headers as `HeaderName`. Conversion copies strings into `GarageCorsRule`.

State/persistence: no direct state; resulting Garage CORS rules are stored in bucket params by callers.

Dependencies/integration: used by S3 bucket CORS handlers and OpenAPI schema generation. Depends on quick-xml-compatible serde attributes and common XML helpers.

Risks: wildcard values are allowed by conversion and may not parse as `HeaderName` for exposed/allowed headers if validation is too strict or too loose; method/header validation must match accepted S3 semantics. Empty CORS rule list is explicitly supported.

Test signals: local tests deserialize sample XML, compare structured values, serialize back, and cover empty configurations.
