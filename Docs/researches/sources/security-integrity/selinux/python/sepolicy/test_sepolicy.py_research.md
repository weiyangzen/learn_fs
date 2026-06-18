# sources/security-integrity/selinux/python/sepolicy/test_sepolicy.py
# sources/security-integrity/selinux/python/sepolicy/test_sepolicy.py

Purpose: integration smoke tests for the installed `sepolicy` CLI.

Important APIs and control flow: `SepolicyTests` defines assertion helpers and test methods that run subprocesses for `sepolicy manpage`, `network`, `transition`, `booleans`, and `interface` commands. The main guard runs tests only when SELinux is enabled and enforcing.

State and persistence: commands may generate manpages or query installed policy; no test cleanup is shown for manpage output because commands use default CLI behavior.

Dependencies and integration points: depends on installed `sepolicy`, SELinux enforcing mode, policy containing common types such as `httpd_t`, `sendmail_t`, `http_port_t`, and booleans like `allow_ypbind`/`nis_enabled`.

Risks and test signals: tests are environment-sensitive and assert only successful exit status, not output correctness. Some assertion code uses old `assert_` APIs. They are useful as broad smoke signals but weak regression tests for content.
