# sources/test-tools/syzkaller/dashboard/app/app.yaml

## Purpose

`app.yaml` is the Google App Engine Standard configuration for the syzkaller dashboard application. It selects the Go runtime, App Engine API compatibility, instance size, inbound mail services, and URL handler routing/security policy.

## Important configuration

- `runtime: go126` selects the Go 1.26 App Engine runtime.
- `app_engine_apis: true` enables legacy App Engine services used by the dashboard code, including datastore, mail, user, and log APIs.
- `instance_class: f4` increases memory relative to `f2`; the comment notes `f2` had soft memory limit crashes.
- `inbound_services` enables `mail` and `mail_bounce`.
- Static handlers serve `/favicon.ico`, `/robots.txt`, and `/static` with `secure: always`.
- Admin-only dynamic handlers cover `/admin`, `/debug/...`, and `/cron/...`.
- `/_ah/mail/...` and `/_ah/bounce` are routed to the app with admin login.
- The catch-all dynamic handler covers root, `/api`, `/bug`, `/text`, `/x/...`, and all other paths with HTTPS required.

## Control flow and integration behavior

Handler order matters: static assets are matched before dynamic catch-all routes, admin/debug/cron routes require admin login, and API/UI/text routes are served by the Go app. The mail routes enable App Engine to deliver inbound email and bounces into registered handlers, which is required by dashboard reporting workflows and tests that simulate incoming email.

## Dependencies and risks

The configuration depends on App Engine Standard semantics for URL handler ordering, login requirements, secure transport, and inbound service names. Misrouting `/api` or `/text` would break manager clients and UI text retrieval. Removing admin protection from debug/cron/admin paths would be a security risk; applying admin login to the catch-all would break public dashboard access and API clients. Reducing instance class could reintroduce memory crashes under request load.

## Test signals

This YAML is not directly unit tested, but the Go test harness depends on equivalent route registration and App Engine API availability. End-to-end tests for API, UI, admin emergency stop, text routes, and email flows provide indirect coverage of the route model represented here.
