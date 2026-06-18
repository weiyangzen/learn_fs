# File Research: sources/local-fs/reiserfsprogs/tune/reiserfstune.8.in

Manual page template for `reiserfstune`.

Major contents:
- Documents journal tuning, journal relocation, bad-block list storage, UUID, label, check interval, last-checked time, max mount count, and mount count.
- Explains current journal device, unavailable journal mode, new journal device, journal size, offset, and transaction size.
- Warns that relocated journal support historically required patched kernels.
- Documents `--make-journal-standard` for converting a non-standard journal back to standard on-main-device layout.
- Provides bad-block replacement/append options.
- Warns about disabling periodic checks.
- Includes example scenarios for moving journals and recovering when an external journal device is lost.

Dependencies and interactions:
- Version placeholder `@PACKAGE_VERSION@` is substituted by the build.
- Installed by `tune/Makefile.am`, with symlinked `tunefs.reiserfs.8`.

Risks and notes:
- Contains several spelling/wording issues, including “tunning”, “filesytem”, and a typo in the bug-report email domain.
- Some option names differ slightly from code naming, e.g. max transaction wording, but intent is clear.
