## sources/object-store/garage/src/api/common/common_error.rs

Purpose: defines shared API error taxonomy and helper traits used by S3/K2V/admin-derived errors.

Important APIs/types/functions: `CommonError` variants map internal, hyper/http, auth, bad request, unsupported, bucket, and header errors. `commonErrorDerivative!` implements conversions for wrapper error enums. `http_status_code`, `aws_code`, `bad_request`, `TryFrom<HelperError>`, `pass_helper_error`, `helper_error_as_internal`, `CommonErrorDerivative`, `OkOrBadRequest`, and `OkOrInternalError` are reused throughout handlers.

Control flow: error mapping classifies Garage quorum/timeout/remote errors as `503`, most internals as `500`, client bad inputs as `400`, auth as `403`, missing buckets as `404`, and conflicts as `409`. Helper errors are either passed through when representable or wrapped as internal messages.

State/persistence: none.

Dependencies/integration: consumed by signature, S3, K2V, CORS, XML validation, and helper code. It bridges `garage_model::helper::error::Error` and `garage_util::error::Error` into API surfaces.

Risks: `pass_helper_error` panics if called with an unrepresentable helper error; callers must only use it where variants are known. AWS error code mapping is shared externally visible behavior.

Test signals: no local tests. It is indirectly exercised by handler tests and error response generation in API crates.
