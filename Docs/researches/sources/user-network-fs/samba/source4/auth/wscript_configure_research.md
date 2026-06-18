# sources/user-network-fs/samba/source4/auth/wscript_configure

Purpose: Waf configure checks for PAM availability in the auth area.

Important checks: `conf.CHECK_HEADERS('security/pam_appl.h')` checks for the PAM application header, and `conf.CHECK_FUNCS_IN('pam_start', 'pam', checklibc=True)` checks for `pam_start` in libpam or libc.

Control flow: executed during configure to populate config symbols consumed by auth-related build code elsewhere.

State/dependencies/integration: writes configure results into Samba's generated configuration cache/headers; no runtime state. Integrates platform PAM discovery with authentication modules that may be built conditionally outside this exact file list.

Risks/test signals: platform-specific PAM layout can affect whether PAM-dependent auth code is compiled. This tiny file has no local validation beyond Waf's check helpers; configure/build success is the main signal.
