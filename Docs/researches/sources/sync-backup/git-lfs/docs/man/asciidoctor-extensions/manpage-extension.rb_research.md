<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/man/asciidoctor-extensions/manpage-extension.rb -->
# sources/sync-backup/git-lfs/docs/man/asciidoctor-extensions/manpage-extension.rb

## Research

This Ruby extension customizes Asciidoctor manpage conversion for Git LFS docs. `GitLFSManPageConverter` subclasses `Asciidoctor::Converter::ManPageConverter`, registers for `manpage`, and overrides `convert_listing`. For listing blocks with role `synopsis`, it removes `.RS` and `.RE` indentation macros, optionally preceded by `.if n`, then drops empty lines.

State is local to conversion. Integration is the documentation build pipeline that renders manpages. Risks include Asciidoctor internal output changing, regex over-removing legitimate lines in synopsis blocks, and only handling listing blocks rather than other synopsis representations. Test signals would be generated manpage diffs for synopsis indentation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/man/asciidoctor-extensions/manpage-extension.rb -->
