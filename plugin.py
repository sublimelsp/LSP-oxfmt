from __future__ import annotations

from LSP.plugin import ClientNotification
from LSP.plugin import ClientResponse
from LSP.plugin import DottedDict
from LSP.plugin import LspPlugin
from LSP.plugin import OnPreStartContext
from LSP.plugin import PluginStartError
from LSP.plugin import ServerResponse
from LSP.plugin import WorkspaceFolder
from lsp_utils import NodeManager
from pathlib import Path
from sublime_lib import ResourcePath
from typing import Any
from typing_extensions import override
import sublime

OXFMT_LOCATION = Path('node_modules', 'oxfmt', 'bin', 'oxfmt')
# The section the server requests with `workspace/configuration`.
SERVER_SECTION = 'oxc_language_server'
# Maps server option names to package setting keys (same as the VSCode extension).
SERVER_OPTIONS = {
    'fmt.configPath': 'oxc.fmt.configPath',
    'fmt.disableNestedConfig': 'oxc.fmt.disableNestedConfig',
}


def to_server_options(settings: DottedDict) -> dict[str, Any]:
    return {option: value for option, key in SERVER_OPTIONS.items() if (value := settings.get(key)) is not None}


class LspOxfmtPlugin(LspPlugin):

    @classmethod
    @override
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        server_path: str | None = context.configuration.root_settings.get('server_path')
        if server_path and server_path != 'auto':
            if (oxfmt_path := cls._get_workspace_relative_path(Path(server_path), context.workspace_folders)):
                context.configuration.root_settings['server_path'] = str(oxfmt_path)
            else:
                raise PluginStartError(
                    f'[LSP-oxfmt] Could not resolve oxfmt binary from specified server_path {server_path}.')
        elif (oxfmt_path := cls._get_workspace_dependency(context.workspace_folders)):
            context.configuration.root_settings['server_path'] = str(oxfmt_path)
        package_name = cls.plugin_storage_path.name
        NodeManager.on_pre_start_async(
            context,
            cls.plugin_storage_path,
            ResourcePath('Packages', package_name, 'language-server'),
            OXFMT_LOCATION,
            node_version_requirement='^20.19.0 || >=22.12.0',
        )

    @classmethod
    def _get_workspace_relative_path(cls, lsp_bin: Path, workspace_folders: list[WorkspaceFolder]) -> Path | None:
        if lsp_bin.is_absolute():
            return lsp_bin
        for folder in workspace_folders:
            if (possible_path := Path(folder.path, lsp_bin)).is_file():
                return possible_path
        return None

    @classmethod
    def _get_workspace_dependency(cls, workspace_folders: list[WorkspaceFolder]) -> Path | None:
        for folder in workspace_folders:
            if (binary_path := Path(folder.path, OXFMT_LOCATION)).is_file():
                return binary_path
        return None

    @override
    def on_pre_send_notification_async(self, notification: ClientNotification) -> None:
        if notification['method'] == 'workspace/didChangeConfiguration':
            # The server treats a non-list `settings` value as the options for all workspace folders.
            settings = notification['params'].get('settings')
            notification['params']['settings'] = to_server_options(DottedDict(settings)) if isinstance(settings, dict) \
                else None

    @override
    def on_pre_send_response_async(self, response: ClientResponse) -> None:
        if response['method'] != 'workspace/configuration' or not (session := self.weaksession()):
            return
        options = sublime.expand_variables(
            to_server_options(session.config.settings), session.window.extract_variables())
        # Modify the list in place as it is the one that is sent to the server.
        for index, item in enumerate(response['params']['items']):
            if item.get('section') == SERVER_SECTION:
                response['result'][index] = options

    @override
    def on_server_response_async(self, response: ServerResponse) -> None:
        if response['method'] == 'initialize':
            if (session := self.weaksession()) and (version := response['result'].get('serverInfo', {}).get('version')):
                session.set_config_status_async(version)


def plugin_loaded() -> None:
    LspOxfmtPlugin.register()


def plugin_unloaded() -> None:
    LspOxfmtPlugin.unregister()
