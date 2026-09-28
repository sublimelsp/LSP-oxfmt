# LSP-oxfmt

[Oxfmt](https://oxc.rs/docs/guide/usage/formatter) support for Sublime Text, provided through the oxfmt language server.

Oxfmt formats JavaScript, TypeScript, JSX, TSX, JSON, JSONC, JSON5, CSS, SCSS, Less, HTML, Vue, Svelte, Angular templates, Handlebars, MJML, Markdown, MDX, YAML, TOML and GraphQL.

## Installation

1. Install [LSP](https://packagecontrol.io/packages/LSP) and [LSP-oxfmt](https://packagecontrol.io/packages/LSP-oxfmt) via Package Control.
2. (Optional but recommended) Install [LSP-file-watcher-chokidar](https://github.com/sublimelsp/LSP-file-watcher-chokidar) via Package Control. The server uses file watching to reload when `.oxfmtrc.json` changes.
3. Restart Sublime.

## Oxfmt resolution

The package uses oxfmt from the project's local dependencies (`node_modules/oxfmt`) when it is present. We recommend to add oxfmt as a project dependency, so that the CLI and the editor use the same version.

You can also set an explicit path with the `server_path` setting. A relative path is resolved against the workspace folder.

If the project has no oxfmt dependency and `server_path` is `auto`, the package uses the oxfmt version that it manages itself.

## Configuration

Open the configuration file with the Command Palette `Preferences: LSP-oxfmt Settings` command or from the Sublime menu.

The settings use the option keys of the [oxc language server](https://github.com/oxc-project/oxc/tree/main/crates/oxc_language_server#workspace-options).

Formatting options are configured in the `.oxfmtrc.json` file of the project. Refer to [Configuring oxfmt](https://oxc.rs/docs/guide/usage/formatter/config).

To disable oxfmt for some file types, override the `selector` setting.

## Usage

To format a document, open the Command Palette and select `LSP: Format File`.

To format on save, open `Preferences: LSP Settings` from the Command Palette and set:

```json
{
    "lsp_format_on_save": true,
}
```

When more than one server can format a file (for example LSP-oxfmt and LSP-biome), `LSP: Format File` asks which server to use and remembers the choice for that syntax. You can also set the formatter in the project settings:

```json
{
    "settings": {
        "LSP": {
            "formatters": {
                "source.ts": "LSP-oxfmt",
            }
        }
    }
}
```
