"""
Define a class to hold configurations.
Borrows and merges stuff from YACS, fvcore, and detectron2
https://github.com/rbgirshick/yacs
https://github.com/facebookresearch/fvcore/
https://github.com/facebookresearch/detectron2/
"""

import ast
import copy
import importlib.util
import io
import logging
import os
from typing import Optional
import yaml
from ast import literal_eval

_YAML_EXTS = {"", ".yml", ".yaml"}
_PY_EXTS = {".py"}
_VALID_TYPES = {tuple, list, str, int, float, bool}
_FILE_TYPES = (io.IOBase)

logger = logging.getLogger(__name__)

class CfgNode(dict):
    r"""CfgNode is a `node` int the configureation `tree`. it simple wrapper around a `dict` and supports access to
    `attributes` via `keys`
    """
    IMMUTABLE = "__immutable__"
    DEPRECATED_KEYS = "__deprecated_keys__"
    RENAMED_KEYS = "__renamed_keys__"
    NEW_ALLOWED = "__new_allowed__"

    def __init__(
        self,
        init_dict: Optional[dict] = None,
        key_list: Optional[list] = None,
        new_allowed: Optional[bool] = False):
        """
        Args:
            init_dict (dict): A dictionary to initialize the `CfgNode`.
            key_list (list[str]): A list of names that index this `CfgNode` from the root. Currently, only used for
                logging.
            new_allowed (bool): Whether adding a new key is allowed when merging with other `CfgNode` objects.
        """

        init_dict = {} if init_dict is None else init_dict
        key_list = [] if key_list is None else key_list
        init_dict = self.__create_config_tree_from_dict(init_dict, key_list)
        super(CfgNode, self).__init__(init_dict)

        # Control the immutability of the `CfgNode`.
        self.__dict__[CfgNode.IMMUTABLE] = False
        # Support for deprecated options.
        # If you choose to remove support for an option in code, but don't want to change all of the config files
        # (to allow for deprecated config files to run), you can add the full config key as a string to this set.
        self.__dict__[CfgNode.DEPRECATED_KEYS] = set()
        # Support for renamed options.
        # If you rename an option, record the mapping from the old name to the new name in this dictionary. Optionally,
        # if the type also changed, you can make this value a tuple that specifies two things: the renamed key, and the
        # instructions to edit the config file.

        self.__dict__[CfgNode.RENAMED_KEYS] = {
            # 'EXAMPLE.OLD.KEY': 'EXAMPLE.NEW.KEY',  # Dummy example
            # 'EXAMPLE.OLD.KEY': (                   # A more complex example
            #     'EXAMPLE.NEW.KEY',
            #     "Also convert to a tuple, eg. 'foo' -> ('foo', ) or "
            #     + "'foo.bar' -> ('foo', 'bar')"
            # ),
        }
        self.__dict__[CfgNode.NEW_ALLOWED] = new_allowed

    @classmethod
    def _create_config_tree_from_dict(
        cls,
        init_dict: dict,
        key_list: list):
        """Create a configuration tree using the input dict. Any dict-like objects inside `init_dict` will be treated
        as new `CfgNode` objects.
        Args:
            init_dict (dict): Input dictionary, to create config tree from.
            key_list (list): A list of names that index this `CfgNode` from the root. Currently only used for logging.
        """
        d = copy.deepcopy(init_dict)
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = cls(v, key_list=key_list + [k])
            else:
                _assert_with_logging(
                    _valid_type(v, allow_cfg_node=False),
                    "Key {} with value {} is not a valid type; valid types: {}".format(
                        ".".join(key_list + [k]), type(v), _VALID_TYPES
                    ),
                )
        return d

    def __getattr__(self, name: str):
        if name in self:
            return self[name]
        else:
            raise AttributeError(name)

    def __setattr__(self, name: str, value):
        if self.is_frozen():
            raise AttributeError(
                "Attempted to set {} to {}, but cfgNode is immutable".format(
                    name, value
                )
            )
        _assert_with_logging(
            name not in self.__dict__,
            "invalid attempt to omdify internatl cfgNoed state: {}".format(
                name
            )
        )
        
        _assert_with_logging(
            _valid_type(value, allow_cfg_node = True),
            "invalid type {} for key {}; valid types = {}".format(
                type(value), name, _VALID_TYPES
            ),
        )
        self[name] = value
    
    def __str__(self):
        def _indent(s_, num_spaces):
            s = s_.split("\n")
            if len(s) == 1:
                return s_
            first = s.pop(0)

            s = [(num_spaces * " ") + line for line in s]
            s = "\n".join(s)
            s = first + "\n" + s
            
            return s

        r = ""
        s = []
        for k, v in sorted(self.items()):
            separator = "\n" if isinstance(v, CfgNode) else " "
            attr_str = "{}:{}{}".format(str(k), separator, str(v))
            attr_str = _indent(attr_str, 2)
            s.append(attr_str)

        r += "\n".join(s)
        return r

def _valid_type(value, allow_cfg_node: Optional[bool] = False):
    return ( type(value) in _VALID_TYPES) or(
        allow_cfg_node and isinstance(value, CfgNode)
    )

def _assert_with_logging(cond, msg):
    if not cond:
        logger.debug(msg)
    assert cond, msg