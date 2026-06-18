
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretManagementEndpoint.java

Purpose: REST resource for generating and revoking S3 secrets.

Important APIs and control flow: class is rooted at `/`, guarded by both `@S3SecretEnabled` and `@S3AdminEndpoint`. `PUT /` generates a secret for the request user; `PUT /{username}` generates for a specified user. `generateInternal` calls object store `getS3Secret`, returns XML-serializable `S3SecretResponse`, and audits success. `OMException.S3_SECRET_ALREADY_EXISTS` maps to 400 with reason text; other OM exceptions log and return 500. `DELETE /` and `DELETE /{username}` revoke for current or supplied user; missing secret maps to 404.

State, dependencies, integration: inherits client/context/audit state from `S3SecretEndpointBase`. Uses `S3SecretValue` from OM, JAX-RS `Response`, `S3GAction` audit constants, and SLF4J logging. Deployed under `/secret/*` by `s3g-web/WEB-INF/web.xml`.

Risks and test signals: path-param username lets admins act on other users, so admin filter correctness is essential. Non-OM `IOException` propagates. `getS3Secret` has create semantics in the client layer, so repeated requests depend on OM duplicate handling. No direct tests in this subset exercise the HTTP secret endpoint.
