import os
import sys

import volatility3.cli
import volatility3.plugins
from volatility3 import framework

volatility3.framework.require_interface_version(2, 0, 0)
failures = framework.import_files(volatility3.plugins, True)

from volatility3.framework import automagic, contexts, interfaces, plugins
from volatility3.framework.constants import ProgressCallback
from volatility3.framework.renderers import NotApplicableValue, UnreadableValue


class MainModel:
    @staticmethod
    def refine_by_type(item):
        match item:
            case UnreadableValue():
                return "-"
            case NotApplicableValue():
                return "N/A"
            case _:
                return item

    def __init__(self):
        self._image_path: str | None = None
        self._results = dict()

    def open_image(self, path: str):
        self._image_path = path
        self._results.clear()

    @staticmethod
    def construct_runner(
        plugin_name: str, image_path: str, progress_callback: ProgressCallback
    ):
        ctx = contexts.Context()
        automagics = automagic.available(ctx)
        plugin_list = framework.list_plugins()
        plugin = plugin_list[plugin_name]
        base_config_path = "plugins"
        ctx.config["automagic.LayerStacker.single_location"] = (
            volatility3.cli.CommandLine.location_from_file(image_path)
        )
        constructed = plugins.construct_plugin(
            ctx,
            automagics,
            plugin,
            base_config_path,
            progress_callback,
            None,
        )
        return constructed

    def run_ps_list(self, progress_callback: ProgressCallback):
        if self._image_path is None:
            return []
        plugin_name = "windows.pslist.PsList"
        if plugin_name in self._results:
            return self._results[plugin_name]
        rows = []
        for _, e in MainModel.construct_runner(
            plugin_name, self._image_path, progress_callback
        )._generator():
            row = list(map(MainModel.refine_by_type, e))
            row[3] = "0x%X" % row[3]
            rows.append(row)
        self._results[plugin_name] = rows
        return rows

    def run_ps_scan(self, progress_callback: ProgressCallback):
        if self._image_path is None:
            return []
        plugin_name = "windows.psscan.PsScan"
        if plugin_name in self._results:
            return self._results[plugin_name]
        rows = []
        for _, e in MainModel.construct_runner(
            plugin_name, self._image_path, progress_callback
        )._generator():
            row = list(map(MainModel.refine_by_type, e))
            row[3] = "0x%X" % row[3]
            rows.append(row)
        self._results[plugin_name] = rows
        return rows


    def run_file_scan(self, progress_callback: ProgressCallback):
        if self._image_path is None:
            return []
        plugin_name = "windows.filescan.FileScan"
        # if plugin_name in self._results:
        #     return self._results[plugin_name]

        return MainModel.construct_runner(
            plugin_name, self._image_path, progress_callback
        )


__all__ = ["MainModel"] 
