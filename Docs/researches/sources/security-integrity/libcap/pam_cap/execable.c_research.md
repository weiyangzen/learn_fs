# sources/security-integrity/libcap/pam_cap/execable.c

Purpose: gives the PAM shared object an executable entry point via `SO_MAIN()` so running `pam_cap.so` directly prints version and help text.

Important APIs/functions: includes `../libcap/execable.h`; `SO_MAIN(int argc, char **argv)` prints `LIBCAP_VERSION`, purpose text, documentation URLs, and optional `--help` module argument documentation. It accepts no functional PAM operations.

Control flow: default invocation prints identity and exits. With exactly `--help`, it also lists supported PAM stack arguments. Any other argument count or value exits with status 1.

State and dependencies: no persistent state; depends on libcap build macros and stdio. It integrates with the module build to provide self-description without loading PAM.

Risks and test signals: risk is documentation drift against `pam_cap.c::parse_args()`. The current help includes `debug`, `config=`, `keepcaps`, `autoauth`, `default=`, and `defer`, matching parser support.
