# sources/test-tools/xfstests-bld/release/README.in

Purpose: release README template for KVM test appliance image bundles. It explains what the images are, where xfstests-bld lives, architecture guidance, quick-start documentation, GPL corresponding-source information, Debian distro source mirror, git repository versions, and image creation scripts.

Important placeholders: `@DISTRO@`, `@MIRROR@`, and `@VERFILE@` are replaced by `gen-README`.

Control flow/state: no executable logic. Generated README persists in `release/out_dir/README`.

Dependencies/integration: consumed by `release/gen-README`, which injects Debian mirror/distro and git version file content.

Risks: stale quick-start URL, distro name, mirror, or git-version data can make release compliance information inaccurate.

Test signals: release generation should verify placeholders are fully replaced and `@VERFILE@` content is present.
