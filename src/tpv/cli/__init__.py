import argparse
import plumbum.cli
import sys

from metachao import aspect
from tpv.ordereddict import OrderedDict


# plumbum stuff we support (so far)
#CountingAttr = plumbum.cli.CountingAttr
Flag = plumbum.cli.Flag
SwitchAttr = plumbum.cli.SwitchAttr
switch = plumbum.cli.switch


# ATTENTION: MONKEY-PATCH
# Meta-switches are active for all subcommands. We don't want -v for
# version, only --version.
plumbum.cli.Application.version._switch_info.names = ['version']


class application(aspect.Aspect):
    @aspect.plumb
    def __call__(_next, self, **kw):
        self._App = self._generate_plumbum_cli_app(node=self,
                                                   main_func=_next._next_method)
        self._app = self._App.run()

    def _generate_plumbum_cli_app(self, node, main_func):
        class App(node.__class__, plumbum.cli.Application):
            main = main_func
            __init__ = plumbum.cli.Application.__init__

        for name, subcommand in node.items():
            subcommand = self._generate_plumbum_cli_app(
                node=subcommand,
                main_func=subcommand.__call__
            )
            subcommand.__name__ = name
            App.subcommand(name)(subcommand)

        return App
