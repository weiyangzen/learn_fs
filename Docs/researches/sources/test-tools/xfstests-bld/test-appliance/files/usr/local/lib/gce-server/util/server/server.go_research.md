# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/server/server.go

Purpose: shared HTTPS server, authentication, request/response schema, internal LTM/KCS RPC, and KCS launch/discovery logic.

Important types/APIs: request enums `RequestType`, `ResultType`; JSON structs `UserOptions`, `InternalOptions`, `TaskRequest`, `SimpleResponse`; server `Instance`; handlers `Login`, `LoginHandler`, `FailureHandler`, `ParseTaskRequest`, `SendResponse`; RPC helpers `SendInternalRequest`, `sendRequest`, `accessKCS`, `runLaunchKCS`, and `fetchLTMConfig`.

Control flow: init loads/generates cookie secret, reads LTM or KCS password from config, verifies project config, and derives TLS client certificate path. `Instance.Start` logs startup through `gce-logger` and serves TLS. User endpoints use cookie sessions; internal endpoints validate shared password in `ExtraOptions`. `SendInternalRequest` discovers peer internal IP config, injects password, sends mTLS-ish HTTPS with `InsecureSkipVerify`, and retries connection attempts. KCS access may launch KCS by running `gce-xfstests launch-kcs`.

State and dependencies: `/usr/local/lib/gce-server/.sessions_secret_key`, lighttpd/server certs, project-specific `.gce_xfstests_cert_*.pem`, generated `.ltm_instance_*`/`.kcs_instance_*`, GCE config, external `gce-xfstests`, and `gce-logger`.

Risks and test signals: TLS skips server verification while using a client certificate. Internal password is copied into request JSON logs. `RequestType.String` omits an element for `Query`, so calling it on `Query` would panic. Tests should cover auth failures, panic handler JSON, internal retry behavior, and KCS launch races.
