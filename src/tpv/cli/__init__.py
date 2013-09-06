import plumbum.cli
import pkg_resources
import sys

from metachao import aspect
from metachao import classtree


# plumbum stuff we support (so far)
#CountingAttr = plumbum.cli.CountingAttr
Flag = plumbum.cli.Flag
SwitchAttr = plumbum.cli.SwitchAttr
autoswitch = plumbum.cli.autoswitch
switch = plumbum.cli.switch

completion = plumbum.cli.completion

Completion = plumbum.cli.Completion
FileCompletion = plumbum.cli.FileCompletion
DirectoryCompletion = plumbum.cli.DirectoryCompletion
ListCompletion = plumbum.cli.ListCompletion
DynamicCompletion = plumbum.cli.DynamicCompletion
CallbackDynamicCompletion = plumbum.cli.CallbackDynamicCompletion

class DictDynamicCompletion(DynamicCompletion):
    def __init__(self, dicttree):
        self.dicttree = dicttree

    def complete(self, command, prefix):
        node = self.dicttree
        components = prefix.split("/")
        for comp in components[:-1]:
            node = node[comp]

        return ["/".join(components[:-1] + [k]) \
                + ("/" if isinstance(v, dict) else "")
                for k,v in node.iteritems() if k.startswith(components[-1])]

    def zsh_action(self, argname):
        return " __xin_complete_path_like %s" % argname


# ATTENTION: MONKEY-PATCH
# Meta-switches are active for all subcommands. We don't want -v for
# version, only --version.
plumbum.cli.Application.version._switch_info.names = ['version']


class setitem_registers_subcommand(aspect.Aspect):
    """Register child as subcommand"""
    @aspect.plumb
    def __setitem__(_next, cls, name, subcommand):
        _next(name, subcommand)
        cls.subcommand(name)(subcommand)


@setitem_registers_subcommand
class command(classtree.node):
    """Metaclass to produce cli apps via nested command classes"""


class Command(plumbum.cli.Application):
    __metaclass__ = command

    CALL_MAIN_IF_NESTED_COMMAND = False

    @property
    def main(self):
        return self.__call__
