<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/wscript_build -->
# sources/user-network-fs/samba/source4/scripting/bin/wscript_build

Purpose: Waf build snippet that registers Samba scripting binaries for installation from `source4/scripting/bin`.

Important APIs/types/functions: `bld.CONFIG_SET`, `bld.SAMBA_SCRIPT`, and build conditionals `AD_DC_BUILD_IS_ENABLED` and `HAVE_ADS`.

Control flow: AD DC builds install DNS/SPN/KCC/provision/downgrade scripts plus `gen_output.py`. ADS builds install `samba-tool`. `samba-gpupdate` is always registered.

State and persistence behavior: affects build metadata and install outputs, not runtime state.

Dependencies and integration points: consumed by the top-level `source4/scripting/wscript_build`, which recurses into `bin`.

Risks: conditional omissions can remove admin tools from builds lacking AD DC or ADS support. Script names must match files.

Test signals: Waf configure/build logs and installed script presence under expected bindir/sbindir.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/wscript_build -->
