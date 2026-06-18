# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/send-mail.py

Purpose: command-line SendGrid mail sender used by shutdown scripts.

Important flow: parse options such as sender and subject, read message body from stdin, build a SendGrid email to one or more recipients, use `SENDGRID_API_KEY` from environment, send, and return an error on API failure.

State and dependencies: no persistent local state; depends on Python 3, SendGrid Python package installed by image build, and environment credentials.

Integration points: `gce-shutdown` invokes it for summary and JUnit emails because shutdown is shell-based while Go services use `util/email`.

Risks and test signals: mail body size can be large when full logs are sent. Credentials must be present in environment. Tests should mock SendGrid client and verify CLI argument parsing and stdin body handling.
