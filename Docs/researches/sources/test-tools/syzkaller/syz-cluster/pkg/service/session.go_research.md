## sources/test-tools/syzkaller/syz-cluster/pkg/service/session.go

`SessionService` manages fuzzing/testing sessions tied to uploaded patch series and optional jobs. Its public methods are `UploadSession`, `TriageResult`, and `GetSessionInfo`; construction wires session, series, job, and blob dependencies from `app.AppEnvironment`.

`UploadSession` resolves an external series ID to an internal series row, creates a session with tags and `CreatedAt`, and returns the generated session ID. `TriageResult` optionally writes triage logs to blob storage and updates session state with the triage log URI and skip reason. `GetSessionInfo` fetches full series data, reloads the session row, and includes job details when `JobID` is set.

State persists in Spanner sessions and blob storage for triage logs. Integration points are the series tracker, triage workflow action, controller HTTP API, and report-generation path. Risks include blob log writes preceding session update, session creation failing if series import has not completed, and `GetSessionInfo` doing full patch-body reads even when only metadata might be needed by some callers. Errors are normalized for missing series/session through shared service errors.
