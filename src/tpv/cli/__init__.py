import argparse
import plumbum.cli
import pkg_resources
import sys

from metachao import aspect


# plumbum stuff we support (so far)
#CountingAttr = plumbum.cli.CountingAttr
Flag = plumbum.cli.Flag
SwitchAttr = plumbum.cli.SwitchAttr
autoswitch = plumbum.cli.autoswitch
switch = plumbum.cli.switch


# ATTENTION: MONKEY-PATCH
# Meta-switches are active for all subcommands. We don't want -v for
# version, only --version.
plumbum.cli.Application.version._switch_info.names = ['version']


class Command(plumbum.cli.Application):
    CALL_MAIN_IF_NESTED_COMMAND = False
    entry_point_group = None

    @property
    def main(self):
        return self.__call__

    def __init__(self, *args, **kw):
        self._subcommand_classes = {'/': self.__class__}
        if self.entry_point_group:
            eps = sorted(pkg_resources.iter_entry_points(self.entry_point_group),
                         key=lambda x: x.name)
            for ep in eps:
                path = ep.name
                if not path.startswith('/'):
                    path = '/' + path
                if not path.endswith('/'):
                    path = path + '/'
                components = path.split('/')
                name = components.pop(-2)
                parent = '/'.join(components)
                Parent = self._subcommand_classes[parent]
                Subcommand = ep.load()
                self._subcommand_classes[path] = Subcommand
                Parent.subcommand(name)(Subcommand)

        plumbum.cli.Application.__init__(self, *args, **kw)
