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
Predicate = plumbum.cli.Predicate

# decorator to mark arguments supporting Completions
completion = plumbum.cli.completion

# Completion Objects, which control the completion of arguments
# refer to plumbum/cli/completion.py
Completion = plumbum.cli.Completion
FileCompletion = plumbum.cli.FileCompletion
DirectoryCompletion = plumbum.cli.DirectoryCompletion
ListCompletion = plumbum.cli.ListCompletion
DynamicCompletion = plumbum.cli.DynamicCompletion
CallbackDynamicCompletion = plumbum.cli.CallbackDynamicCompletion


class DictDynamicCompletion(DynamicCompletion):
    '''Completion class to dynamically complete paths in a dicttree

uses / as a separator (obviously).

Usage example:

    PROFILE=dict(foo=dict(foo1=1, foo2=2), bar=3)
    class profile(tpv.cli.Command):
        @tpv.cli.completion(name=tpv.cli.DictDynamicCompletion(PROFILE))
        def __call__(self, name):
            [...]

then on the command line

    xin profile foo/foTAB

should give foo1 and foo2 as completions.
    '''
    def __init__(self, dicttree):
        self.dicttree = dicttree

    def complete(self, command, prefix):
        # traverse node into dicttree
        node = self.dicttree
        components = prefix.split("/")
        for comp in components[:-1]:
            node = node[comp]

        # return list of possible matches with the full path
        return ["/".join(components[:-1] + [k]) \
                + ("/" if isinstance(v, dict) else "")
                for k, v in node.iteritems()
                if k.startswith(components[-1])]

    def zsh_action(self, argname):
        # use a path like completion, then zsh completes
        # /foo/foTAB to /foo/foo and displays foo1 foo2
        return " __xin_complete_path_like %s" % argname


class DocPredicate(object):
    """A wrapper for a single-argument function with pretty printing"""
    def __init__(self, func):
        self.func = func

    def __str__(self):
        return self.func.__doc__ \
            if self.func.__doc__ is not None \
            else self.func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


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


# always use CompletionMixin
class Command(plumbum.cli.Application, plumbum.cli.CompletionMixin):
    __metaclass__ = command

    CALL_MAIN_IF_NESTED_COMMAND = False

    @property
    def main(self):
        return self.__call__
