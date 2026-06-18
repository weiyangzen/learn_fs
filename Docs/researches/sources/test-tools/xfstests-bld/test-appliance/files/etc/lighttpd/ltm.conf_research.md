# sources/test-tools/xfstests-bld/test-appliance/files/etc/lighttpd/ltm.conf

- Purpose: lighttpd LTM web configuration; it sets the LTM web document root, CGI support, and index handling for the management UI. The file is 11 lines/303 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/lighttpd/ltm.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements XML or single-purpose config entries; key lines include server.document-root        = "/var/www", index-file.names            := ( "index.shtml", "index.html" ), mimetype.assign = (, ".htm" => "text/html",, ".html" => "text/html",, ".shtml" => "text/html",, "" => "text/plain" ), static-file.exclude-extensions += ( ".shtml" ).
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
