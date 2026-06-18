# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/spec.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/spec.py

Purpose: RPM spec file template fragments for packaging generated SELinux policy modules.

Important APIs and control flow: defines `header_comment_section`, `base_section`, and `mid_section` for package metadata, build requirements, `%prep`, `%build`, `%install`, `%check`, `%post`, `%postun`, `%files`, and changelog scaffolding. Also defines relabel macro fragments `define_relabel_files_begin` and `define_relabel_files_end`.

State and persistence: rendered into RPM spec files that build policy modules, install `.pp`, interface, manpage, and script artifacts, and invoke semodule/relabel commands in package scriptlets.

Dependencies and integration points: depends on RPM macros, SELinux policy module packaging conventions, `semodule`, `restorecon`, `make`, and `selinux-policy-devel`.

Risks and test signals: generated `%post` scriptlets can affect host policy during package install/upgrade/removal; spec correctness depends on placeholder substitution and file list completeness. No direct tests validate generated RPMs.
